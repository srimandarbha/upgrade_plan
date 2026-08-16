"""Red Hat Security Data API collector -> advisories table.

Covers the two feeds from your pre-check doc:
    CVE endpoint : https://access.redhat.com/hydra/rest/securitydata/cve.json
    CSAF/errata  : https://access.redhat.com/hydra/rest/securitydata/csaf.json

Both are public, unauthenticated JSON endpoints reachable from your bastion.
Run this on the connected side; ship the resulting DB rows (or a JSON export,
see `export_since()`) across the air gap through your normal mirror pipeline.

NOTE ON FIELD NAMES: this parses the response shape Red Hat documents at
https://access.redhat.com/solutions/6979472. Hydra's JSON responses have
drifted slightly between API generations before, so the first time you point
this at a live endpoint, log one raw response and diff it against
`_parse_cve_item` / `_parse_csaf_item` below -- both are written defensively
(`.get()` everywhere) specifically so a missing/renamed field degrades to
`None` instead of throwing.
"""
from __future__ import annotations

import argparse
import logging
from datetime import datetime, timezone

import requests
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from db.db import get_session
from db.models import Advisory

log = logging.getLogger(__name__)

CVE_ENDPOINT = "https://access.redhat.com/hydra/rest/securitydata/cve.json"
CSAF_ENDPOINT = "https://access.redhat.com/hydra/rest/securitydata/csaf.json"

# Products worth tracking for an OCV (OpenShift Virtualization) + Dell CSM +
# Portworx fleet. Extend as your operator inventory grows.
DEFAULT_PRODUCTS = [
    "openshift-container-platform",
    "openshift-virtualization",
]


def fetch_cves(
    product: str,
    severity: str | None = None,
    after: str | None = None,
    session: requests.Session | None = None,
) -> list[dict]:
    """GET the CVE feed for one product, optionally filtered by severity/date."""
    params = {"product": product}
    if severity:
        params["severity"] = severity
    if after:
        params["after"] = after
    http = session or requests
    resp = http.get(CVE_ENDPOINT, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_csaf(
    severity: str | None = None,
    after: str | None = None,
    session: requests.Session | None = None,
) -> list[dict]:
    """GET the CSAF/errata index, optionally filtered by severity/date."""
    params = {}
    if severity:
        params["severity"] = severity
    if after:
        params["after"] = after
    http = session or requests
    resp = http.get(CSAF_ENDPOINT, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _parse_dt(value) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def _parse_cve_item(item: dict, affected_component: str) -> dict:
    return {
        "source": "redhat-cve",
        "external_id": item.get("CVE") or item.get("cve") or item.get("id", "UNKNOWN"),
        "title": item.get("bugzilla", {}).get("description") or item.get("CVE", "CVE"),
        "severity": (item.get("severity") or item.get("threat_severity") or "").lower() or None,
        "affected_component": affected_component,
        "affected_version_range": None,  # filled in by operator_compat cross-reference downstream
        "published_at": _parse_dt(item.get("public_date")),
        "url": item.get("resource_url"),
        "raw": item,
    }


def _parse_csaf_item(item: dict, affected_component: str) -> dict:
    csaf_id = item.get("RHSA") or item.get("id") or item.get("CVE") or item.get("name") or "UNKNOWN"
    title = item.get("title") or item.get("RHSA") or csaf_id
    pub_date = item.get("released_on") or item.get("current_release_date") or item.get("initial_release_date")
    url = item.get("resource_url") or item.get("self_href") or f"https://access.redhat.com/errata/{csaf_id}"
    return {
        "source": "redhat-errata",
        "external_id": csaf_id,
        "title": title,
        "severity": (item.get("severity") or "").lower() or None,
        "affected_component": affected_component,
        "affected_version_range": None,
        "published_at": _parse_dt(pub_date),
        "url": url,
        "raw": item,
    }


def upsert_advisories(session: Session, rows: list[dict]) -> int:
    """Upsert on (source, external_id). Returns count written."""
    if not rows:
        return 0
    dialect = session.get_bind().dialect.name
    insert_fn = pg_insert if dialect == "postgresql" else sqlite_insert
    stmt = insert_fn(Advisory).values(rows)
    update_cols = {c: getattr(stmt.excluded, c) for c in rows[0] if c not in ("source", "external_id")}
    stmt = stmt.on_conflict_do_update(
        index_elements=["source", "external_id"], set_=update_cols
    )
    session.execute(stmt)
    return len(rows)


def collect(products: list[str] | None = None, severity: str | None = None, after: str | None = None) -> int:
    products = products or DEFAULT_PRODUCTS
    total = 0
    with get_session() as db:
        for product in products:
            component = "ocv" if "virtualization" in product else "ocp"
            try:
                cves = fetch_cves(product, severity=severity, after=after)
            except requests.RequestException as exc:
                log.warning("CVE fetch failed for %s: %s", product, exc)
                continue
            rows = [_parse_cve_item(c, component) for c in cves]
            total += upsert_advisories(db, rows)

        try:
            errata = fetch_csaf(severity=severity, after=after)
            rows = [_parse_csaf_item(e, "ocp") for e in errata]
            total += upsert_advisories(db, rows)
        except requests.RequestException as exc:
            log.warning("CSAF fetch failed: %s", exc)
    return total


def main():
    logging.basicConfig(level=logging.INFO)
    ap = argparse.ArgumentParser(description="Pull Red Hat CVE/errata data into advisories table")
    ap.add_argument("--product", action="append", help="repeatable; default: OCP + OCV")
    ap.add_argument("--severity", choices=["low", "moderate", "important", "critical"])
    ap.add_argument("--after", help="YYYY-MM-DD; only advisories published after this date")
    args = ap.parse_args()
    n = collect(products=args.product, severity=args.severity, after=args.after)
    log.info("Upserted %d advisories", n)


if __name__ == "__main__":
    main()
