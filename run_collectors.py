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

from db.db import init_db

log = logging.getLogger(__name__)

COLLECTORS = {
    "redhat-security": "collectors.redhat_security",
    "lifecycle": "collectors.lifecycle",
    "cincinnati": "collectors.cincinnati",
    "vendor-matrix": "collectors.vendor_matrix",
    "cluster-state": "collectors.cluster_state",
    "release-info": "collectors.release_info",
}


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description="Run OCV upgrade agent collectors")
    ap.add_argument(
        "--only",
        help=f"comma-separated subset of: {', '.join(COLLECTORS)} (default: all)",
    )
    ap.add_argument("--cluster", action="append", help="passed through to cluster-state")
    ap.add_argument("--db-url", help="overrides $DATABASE_URL for this run")
    args, unknown = ap.parse_known_args()

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
            else:
                n = module.collect()
            log.info("--- %s done: %s ---", name, n)
        except Exception:  # noqa: BLE001 - one bad collector shouldn't stop the rest
            log.exception("collector %s failed", name)


if __name__ == "__main__":
    main()
