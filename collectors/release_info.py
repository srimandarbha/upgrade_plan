"""`oc adm release info` collector -> release_images table.

Inspects mirrored OpenShift release payloads. In disconnected / air-gapped
environments, supply `--icsp-file` (or `--idms-file`) and `-a` (pull secret)
to resolve digests against your internal mirror registry.

Two modes supported:
- `-o json` gives the payload ImageStream references for `release_images` table.
- `--commits <from> <to>` outputs human-readable commit and bug differences.
"""
from __future__ import annotations

import argparse
import json
import logging
import subprocess
from pathlib import Path

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from db.db import get_session
from db.models import ReleaseImage

log = logging.getLogger(__name__)


def _build_mirror_flags(
    pull_secret: str | Path | None = None,
    icsp_file: str | Path | None = None,
    idms_file: str | Path | None = None,
) -> list[str]:
    flags = []
    if pull_secret:
        flags.extend(["-a", str(pull_secret)])
    if icsp_file:
        flags.append(f"--icsp-file={icsp_file}")
    if idms_file:
        flags.append(f"--idms-file={idms_file}")
    return flags


def fetch_release_metadata(
    version: str,
    oc_binary: str = "oc",
    pull_secret: str | Path | None = None,
    icsp_file: str | Path | None = None,
    idms_file: str | Path | None = None,
) -> dict:
    cmd = [oc_binary, "adm", "release", "info", version, "-o", "json"]
    cmd.extend(_build_mirror_flags(pull_secret, icsp_file, idms_file))
    proc = subprocess.run(
        cmd,
        capture_output=True, text=True, timeout=120,
    )
    proc.check_returncode()
    return json.loads(proc.stdout)


def fetch_commits_raw(
    from_version: str,
    to_version: str,
    oc_binary: str = "oc",
    pull_secret: str | Path | None = None,
    icsp_file: str | Path | None = None,
    idms_file: str | Path | None = None,
) -> str:
    """Human-readable component commit diff (works offline with ICSP/IDMS and local registry pullspec)."""
    cmd = [oc_binary, "adm", "release", "info", from_version, to_version, "--commits"]
    cmd.extend(_build_mirror_flags(pull_secret, icsp_file, idms_file))
    proc = subprocess.run(
        cmd,
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
    stmt = pg_insert(ReleaseImage).values(rows)
    update_cols = {c: getattr(stmt.excluded, c) for c in rows[0] if c not in ("version", "component")}
    stmt = stmt.on_conflict_do_update(index_elements=["version", "component"], set_=update_cols)
    session.execute(stmt)
    return len(rows)


def collect(
    versions: list[str] | str | None = None,
    oc_binary: str = "oc",
    pull_secret: str | Path | None = None,
    icsp_file: str | Path | None = None,
    idms_file: str | Path | None = None,
) -> int:
    if not versions:
        log.info("No target release version provided for release-info collector; skipping.")
        return 0
    if isinstance(versions, str):
        versions = [versions]

    total = 0
    with get_session() as db:
        for version in versions:
            try:
                metadata = fetch_release_metadata(
                    version,
                    oc_binary=oc_binary,
                    pull_secret=pull_secret,
                    icsp_file=icsp_file,
                    idms_file=idms_file,
                )
            except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError) as exc:
                log.warning("release info failed for %s: %s", version, exc)
                continue
            rows = parse_release_images(metadata)
            total += upsert_release_images(db, rows)
    return total


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description="Collect release image inventory via `oc adm release info`")
    ap.add_argument("version", help="release payload version/pullspec to inspect (e.g. registry.local:5000/ocp-release:4.22.8-x86_64)")
    ap.add_argument("--oc-binary", default="oc")
    ap.add_argument("-a", "--pull-secret", help="path to local registry pull secret JSON")
    ap.add_argument("--icsp-file", help="path to ImageContentSourcePolicy YAML file")
    ap.add_argument("--idms-file", help="path to ImageDigestMirrorSet YAML file")
    ap.add_argument(
        "--commits-from", help="if set (with --commits-to), print the raw commit diff and exit"
    )
    ap.add_argument("--commits-to")
    args = ap.parse_args()

    if args.commits_from and args.commits_to:
        diff = fetch_commits_raw(
            args.commits_from,
            args.commits_to,
            oc_binary=args.oc_binary,
            pull_secret=args.pull_secret,
            icsp_file=args.icsp_file,
            idms_file=args.idms_file,
        )
        print(diff)
        return

    n = collect(
        args.version,
        oc_binary=args.oc_binary,
        pull_secret=args.pull_secret,
        icsp_file=args.icsp_file,
        idms_file=args.idms_file,
    )
    log.info("Upserted %d release_images rows for %s", n, args.version)


if __name__ == "__main__":
    main()

