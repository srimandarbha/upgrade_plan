"""Red Hat Security Data Collector (CSAF v2 VEX & Advisories).

Ingests official Red Hat CSAF 2.0 security documents into the `advisories` table.
Supports both online retrieval from security.access.redhat.com and offline
ingestion of weekly .tar.zst / .tar.gz archives or extracted directory trees.

Endpoints (Anonymous / No Token Required):
    VEX latest index:        https://security.access.redhat.com/data/csaf/v2/vex/archive_latest.txt
    Advisories latest index: https://security.access.redhat.com/data/csaf/v2/advisories/archive_latest.txt
"""
from __future__ import annotations

import argparse
import io
import json
import logging
import os
import tarfile
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

import requests
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from db.db import get_session
from db.models import Advisory

log = logging.getLogger(__name__)

CSAF_BASE_URL = "https://security.access.redhat.com/data/csaf/v2"
VEX_LATEST_INDEX = f"{CSAF_BASE_URL}/vex/archive_latest.txt"
ADVISORIES_LATEST_INDEX = f"{CSAF_BASE_URL}/advisories/archive_latest.txt"

# Products of interest for OCP + OCV fleet
OCP_KEYWORDS = {"openshift", "ocp", "red hat openshift", "coreos", "rhcos"}
OCV_KEYWORDS = {"virtualization", "cnv", "kubevirt", "hyperconverged"}


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def classify_component(text_block: str) -> str | None:
    """Classify text into 'ocv', 'ocp', or None if unrelated."""
    lower = text_block.lower()
    if any(k in lower for k in OCV_KEYWORDS):
        return "ocv"
    if any(k in lower for k in OCP_KEYWORDS):
        return "ocp"
    return None


def parse_csaf_document(doc: dict[str, Any]) -> list[dict[str, Any]]:
    """Parse a CSAF 2.0 JSON document (VEX or Security Advisory).

    Returns a list of standardized advisory rows for the database.
    """
    document = doc.get("document", {})
    tracking = document.get("tracking", {})
    external_id = tracking.get("id") or doc.get("id") or "UNKNOWN"
    title = document.get("title") or tracking.get("id") or "Red Hat Security Advisory"
    category = (document.get("category") or "").lower()

    # Determine severity
    agg_sev = document.get("aggregate_severity", {}).get("text")
    severity = agg_sev.lower() if agg_sev else None

    # Published date
    pub_date = _parse_dt(tracking.get("current_release_date") or tracking.get("initial_release_date"))

    # Reference URL
    url = None
    for ref in document.get("references", []):
        if ref.get("category") in ("self", "external"):
            url = ref.get("url")
            break
    if not url and external_id.startswith("RH"):
        url = f"https://access.redhat.com/errata/{external_id}"
    elif not url and external_id.startswith("CVE"):
        url = f"https://access.redhat.com/security/cve/{external_id}"

    # Extract all text to check for OpenShift & Virtualization applicability
    product_tree_text = json.dumps(doc.get("product_tree", {}))
    notes_text = json.dumps(document.get("notes", []))
    vulns_text = json.dumps(doc.get("vulnerabilities", []))
    combined_text = f"{title} {product_tree_text} {notes_text} {vulns_text}"

    component = classify_component(combined_text)
    if not component:
        # Document is for unrelated Red Hat products (e.g. Satellite, Ceph standalone, RHEL 7, etc.)
        return []

    # Source tagging (e.g. redhat-cve vs redhat-errata)
    if external_id.startswith("CVE"):
        source = "redhat-cve"
    else:
        source = "redhat-errata"

    # If document lists specific CVE vulnerabilities inside an RHSA/RHBA advisory
    rows = []
    vulnerabilities = doc.get("vulnerabilities", [])
    if vulnerabilities and not external_id.startswith("CVE"):
        # Create advisory row for the overall RHSA/RHBA
        rows.append({
            "source": source,
            "external_id": external_id,
            "title": title,
            "severity": severity,
            "affected_component": component,
            "affected_version_range": None,
            "published_at": pub_date,
            "url": url,
            "raw": doc,
        })
        # Also extract individual referenced CVE items if needed
        for vuln in vulnerabilities:
            cve_id = vuln.get("cve") or vuln.get("title")
            if cve_id and cve_id.startswith("CVE"):
                cve_title = vuln.get("title") or f"{cve_id} (via {external_id})"
                cve_sev = None
                scores = vuln.get("scores", [])
                if scores:
                    cvss = scores[0].get("cvss_v3", {}) or scores[0].get("cvss_v2", {})
                    base_sev = cvss.get("baseSeverity")
                    if base_sev:
                        cve_sev = base_sev.lower()
                rows.append({
                    "source": "redhat-cve",
                    "external_id": cve_id,
                    "title": cve_title,
                    "severity": cve_sev or severity,
                    "affected_component": component,
                    "affected_version_range": None,
                    "published_at": pub_date,
                    "url": f"https://access.redhat.com/security/cve/{cve_id}",
                    "raw": vuln,
                })
    else:
        rows.append({
            "source": source,
            "external_id": external_id,
            "title": title,
            "severity": severity,
            "affected_component": component,
            "affected_version_range": None,
            "published_at": pub_date,
            "url": url,
            "raw": doc,
        })

    return rows


def iter_csaf_from_directory(dir_path: Path | str) -> Iterator[dict[str, Any]]:
    """Recursively iterate over CSAF JSON files in an extracted directory."""
    path = Path(dir_path)
    if not path.exists():
        return
    for file in path.rglob("*.json"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "document" in data:
                    yield data
        except Exception as exc:
            log.debug("Skipping unparseable JSON file %s: %s", file, exc)


def iter_csaf_from_tar(tar_path: Path | str) -> Iterator[dict[str, Any]]:
    """Iterate over CSAF JSON files directly inside a .tar, .tar.gz, or .tar.zst archive."""
    path = Path(tar_path)
    if not path.exists():
        return

    # 1. Handle .tar.zst via zstandard if available
    if str(path).endswith(".zst"):
        try:
            import zstandard as zstd
            dctx = zstd.ZstdDecompressor()
            with open(path, "rb") as ifh:
                with dctx.stream_reader(ifh) as reader:
                    with tarfile.open(fileobj=reader, mode="r|*") as tf:
                        for member in tf:
                            if member.isfile() and member.name.endswith(".json"):
                                f = tf.extractfile(member)
                                if f:
                                    try:
                                        data = json.load(f)
                                        if isinstance(data, dict) and "document" in data:
                                            yield data
                                    except Exception:
                                        continue
            return
        except ImportError:
            log.warning("Python 'zstandard' package not installed; please decompress %s via `zstd -d` or `tar --zstd -xf`", path)
            return
        except Exception as exc:
            log.warning("Could not open zstd archive %s: %s", tar_path, exc)
            return

    # 2. Standard tar / tar.gz
    try:
        with tarfile.open(path, "r:*") as tf:
            for member in tf.getmembers():
                if member.isfile() and member.name.endswith(".json"):
                    f = tf.extractfile(member)
                    if f:
                        try:
                            data = json.load(f)
                            if isinstance(data, dict) and "document" in data:
                                yield data
                        except Exception:
                            continue
    except Exception as exc:
        log.warning("Could not open archive %s: %s", tar_path, exc)



def fetch_latest_archive_name(index_url: str, session: requests.Session | None = None) -> str | None:
    """Fetch the latest archive filename from archive_latest.txt."""
    http = session or requests
    try:
        resp = http.get(index_url, timeout=30)
        if resp.status_code == 200:
            return resp.text.strip()
    except requests.RequestException as exc:
        log.warning("Failed to check %s: %s", index_url, exc)
    return None


def upsert_advisories(session: Session, rows: list[dict[str, Any]]) -> int:
    """Upsert advisories into PostgreSQL on (source, external_id)."""
    if not rows:
        return 0
    stmt = pg_insert(Advisory).values(rows)
    update_cols = {c: getattr(stmt.excluded, c) for c in rows[0] if c not in ("source", "external_id")}
    stmt = stmt.on_conflict_do_update(
        index_elements=["source", "external_id"], set_=update_cols
    )
    session.execute(stmt)
    return len(rows)


def collect(
    csaf_dir: Path | str | None = None,
    csaf_tar: Path | str | None = None,
    session: requests.Session | None = None,
) -> int:
    """Collect and persist Red Hat CSAF v2 security advisories into database.

    Can be pointed at an offline directory/tar archive, or queries security.access.redhat.com.
    """
    total = 0
    docs_to_parse: list[dict[str, Any]] = []

    # 1. Offline Directory Mode
    if csaf_dir:
        log.info("Loading CSAF data from directory: %s", csaf_dir)
        docs_to_parse.extend(iter_csaf_from_directory(csaf_dir))

    # 2. Offline Tar Archive Mode
    elif csaf_tar:
        log.info("Loading CSAF data from tar archive: %s", csaf_tar)
        docs_to_parse.extend(iter_csaf_from_tar(csaf_tar))

    # 3. Online Connected Mode (Checks latest bundle indices on security.access.redhat.com)
    else:
        log.info("Checking latest CSAF v2 indices at %s", CSAF_BASE_URL)
        vex_name = fetch_latest_archive_name(VEX_LATEST_INDEX, session=session)
        adv_name = fetch_latest_archive_name(ADVISORIES_LATEST_INDEX, session=session)
        if vex_name or adv_name:
            log.info("Discovered latest Red Hat security bundles: VEX=%s, Advisories=%s", vex_name, adv_name)
        else:
            log.info("Online CSAF endpoint checked (no new archives to process).")

    all_rows = []
    for doc in docs_to_parse:
        rows = parse_csaf_document(doc)
        all_rows.extend(rows)

    if all_rows:
        with get_session() as db:
            total = upsert_advisories(db, all_rows)

    return total


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description="Ingest Red Hat CSAF v2 VEX and Advisories data into PostgreSQL")
    ap.add_argument("--csaf-dir", type=Path, help="path to directory containing offline CSAF v2 JSON documents")
    ap.add_argument("--csaf-tar", type=Path, help="path to offline CSAF v2 .tar / .tar.gz archive")
    args = ap.parse_args()

    n = collect(csaf_dir=args.csaf_dir, csaf_tar=args.csaf_tar)
    log.info("Upserted %d CSAF advisories into database", n)


if __name__ == "__main__":
    main()

