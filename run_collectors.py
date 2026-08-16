#!/usr/bin/env python3
"""Entry point for running all (or selected) collectors -- this is what your
CronJob/scheduled Job invokes.

Split by network reachability, matching the bastion / disconnected split in
the architecture: run with --only redhat-security,lifecycle,cincinnati on the
connected bastion, ship the resulting DB (or a pg_dump / row export) across
the air gap, then run --only cluster-state,vendor-matrix,release-info inside
the disconnected network where the clusters and mirrored release payloads
actually are.

Examples:
    python run_collectors.py --only redhat-security,lifecycle,cincinnati
    python run_collectors.py --only cluster-state --cluster east-prod-01
"""
from __future__ import annotations

import argparse
import logging

log = logging.getLogger(__name__)

COLLECTORS = {
    "redhat-security": "collectors.redhat_security",
    "lifecycle": "collectors.lifecycle",
    "cincinnati": "collectors.cincinnati",
    "cincinatti": "collectors.cincinnati",  # alias for common spelling
    "vendor-matrix": "collectors.vendor_matrix",
    "cluster-state": "collectors.cluster_state",
    "release-info": "collectors.release_info",
}


EPILOG = """
examples:
  # Pull only security advisories and product lifecycle dates:
  python run_collectors.py --only redhat-security,lifecycle

  # Filter critical/important security advisories released after a date:
  python run_collectors.py --only redhat-security --severity critical --after 2026-01-01

  # Pull upgrade graph for a specific channel into DB:
  python run_collectors.py --only cincinnati --channel stable-4.22

  # Inspect a specific release payload version via `oc adm release info`:
  python run_collectors.py --only release-info --release-version 4.22.0

  # Run all bastion collectors:
  python run_collectors.py --only redhat-security,lifecycle,cincinnati

  # Run disconnected collectors against a specific cluster and release:
  python run_collectors.py --only cluster-state,vendor-matrix,release-info --cluster east-prod-01 --release-version 4.22.0
"""


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(
        description="Run OCV upgrade agent collectors to populate Postgres / SQLite database.",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument(
        "--only",
        help=f"comma-separated subset of: {', '.join(COLLECTORS)} (default: all)",
    )
    ap.add_argument("--cluster", action="append", help="passed through to cluster-state")
    ap.add_argument("--release-version", action="append", help="target release version(s) for release-info (e.g. 4.22.0)")
    ap.add_argument("--channel", action="append", help="channels for cincinnati (e.g. stable-4.22)")
    ap.add_argument("--product", action="append", help="product(s) for redhat-security (default: OCP + OCV)")
    ap.add_argument("--severity", choices=["low", "moderate", "important", "critical"], help="filter redhat-security by severity")
    ap.add_argument("--after", help="filter redhat-security by published date YYYY-MM-DD")
    ap.add_argument("--db-url", help="overrides $DATABASE_URL for this run")
    args, unknown = ap.parse_known_args()

    from db.db import init_db

    init_db(args.db_url)

    selected = args.only.split(",") if args.only else list(COLLECTORS)
    for name in selected:
        if name not in COLLECTORS:
            log.error("Unknown collector %r, skipping. Valid: %s", name, list(COLLECTORS))
            continue
        module = __import__(COLLECTORS[name], fromlist=["collect"])
        log.info("--- running %s ---", name)
        try:
            if name == "cluster-state":
                n = module.collect(cluster_names=args.cluster)
            elif name == "release-info":
                n = module.collect(versions=args.release_version)
            elif name == "cincinnati":
                n = module.collect(channels=args.channel)
            elif name == "redhat-security":
                n = module.collect(products=args.product, severity=args.severity, after=args.after)
            else:
                n = module.collect()
            log.info("--- %s done: %s ---", name, n)
        except Exception:  # noqa: BLE001 - one bad collector shouldn't stop the rest
            log.exception("collector %s failed", name)


if __name__ == "__main__":
    main()
