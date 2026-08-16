"""`oc adm release info` collector -> release_images table.

Covers point 5/6 from your original pre-check doc for a disconnected
environment: inspecting a mirrored release payload directly instead of
scraping web pages. Two things intentionally kept separate:

- `-o json` gives a stable, well-known structure (an OpenShift release
  payload's `references` field is literally an ImageStream) -- this is what
  we parse and persist, as `release_images`, for feeding an image vulnerability
  scanner per component.

- `--commits <from> <to>` gives a human-readable component-by-component commit
  diff. Its exact column layout isn't a documented/stable contract the way the
  JSON output is, so this module surfaces the raw text for a human to read (or
  paste into a PR description) rather than parsing it into DB rows -- for a
  structured "what bugs did this fix" answer, cross-reference the
  `redhat-errata` rows from redhat_security.py instead, since RHBA/RHSA
  content is the actual source of truth for that.
"""
from __future__ import annotations

import argparse
import json
import logging
import subprocess

from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from db.db import get_session
from db.models import ReleaseImage

log = logging.getLogger(__name__)


def fetch_release_metadata(version: str, oc_binary: str = "oc") -> dict:
    proc = subprocess.run(
        [oc_binary, "adm", "release", "info", version, "-o", "json"],
        capture_output=True, text=True, timeout=120,
    )
    proc.check_returncode()
    return json.loads(proc.stdout)


def fetch_commits_raw(from_version: str, to_version: str, oc_binary: str = "oc") -> str:
    """Human-readable component commit diff -- not parsed, just returned as text."""
    proc = subprocess.run(
        [oc_binary, "adm", "release", "info", from_version, to_version, "--commits"],
        capture_output=True, text=True, timeout=120,
    )
    proc.check_returncode()
    return proc.stdout


def parse_release_images(metadata: dict) -> list[dict]:
    version = metadata.get("metadata", {}).get("version", "unknown")
    tags = metadata.get("references", {}).get("spec", {}).get("tags", [])
    rows = []
    for tag in tags:
        image = (tag.get("from") or {}).get("name")
        component = tag.get("name")
        if component and image:
            rows.append({"component": component, "version": version, "image": image})
    return rows


def upsert_release_images(session: Session, rows: list[dict]) -> int:
    if not rows:
        return 0
    dialect = session.get_bind().dialect.name
    insert_fn = pg_insert if dialect == "postgresql" else sqlite_insert
    stmt = insert_fn(ReleaseImage).values(rows)
    update_cols = {c: getattr(stmt.excluded, c) for c in rows[0] if c not in ("version", "component")}
    stmt = stmt.on_conflict_do_update(index_elements=["version", "component"], set_=update_cols)
    session.execute(stmt)
    return len(rows)


def collect(versions: list[str] | str | None = None, oc_binary: str = "oc") -> int:
    if not versions:
        log.info("No target release version provided for release-info collector; skipping.")
        return 0
    if isinstance(versions, str):
        versions = [versions]

    total = 0
    with get_session() as db:
        for version in versions:
            try:
                metadata = fetch_release_metadata(version, oc_binary=oc_binary)
            except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError) as exc:
                log.warning("release info failed for %s: %s", version, exc)
                continue
            rows = parse_release_images(metadata)
            total += upsert_release_images(db, rows)
    return total


def main():
    logging.basicConfig(level=logging.INFO)
    ap = argparse.ArgumentParser(description="Collect release image inventory via `oc adm release info`")
    ap.add_argument("version", help="release payload version/pullspec to inspect")
    ap.add_argument("--oc-binary", default="oc")
    ap.add_argument(
        "--commits-from", help="if set (with --commits-to), print the raw commit diff and exit"
    )
    ap.add_argument("--commits-to")
    args = ap.parse_args()

    if args.commits_from and args.commits_to:
        print(fetch_commits_raw(args.commits_from, args.commits_to, oc_binary=args.oc_binary))
        return

    n = collect(args.version, oc_binary=args.oc_binary)
    log.info("Upserted %d release_images rows for %s", n, args.version)


if __name__ == "__main__":
    main()
