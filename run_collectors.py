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
    python run_collectors.py --only release-info --release-version registry.local:5000/ocp-release:4.22.8-x86_64 --icsp-file=icsp.yaml -a pull-secret.json
    python run_collectors.py --only redhat-security --csaf-dir /path/to/offline/csaf/
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

from db.db import init_db

log = logging.getLogger(__name__)

COLLECTORS = {
    "redhat-security": "collectors.redhat_security",
    "lifecycle": "collectors.lifecycle",
    "cincinnati": "collectors.cincinnati",
    "vendor-matrix": "collectors.vendor_matrix",
    "cluster-state": "collectors.cluster_state",
    "release-info": "collectors.release_info",
    "gitops-inventory": "collectors.gitops_inventory",
}


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description="Run OCV upgrade agent collectors")
    ap.add_argument(
        "--only",
        help=f"comma-separated subset of: {', '.join(COLLECTORS)} (default: all)",
    )
    ap.add_argument("--cluster", action="append", help="passed through to cluster-state")
    ap.add_argument("--release-version", action="append", help="target release version(s)/pullspecs for release-info")
    ap.add_argument("-a", "--pull-secret", help="path to local registry pull secret JSON for release-info")
    ap.add_argument("--vault-pull-secret-path", help="Vault secret path to fetch pull secret from (e.g. secret/data/registry/pull-secret)")
    ap.add_argument("--icsp-file", help="path to ImageContentSourcePolicy YAML for release-info")
    ap.add_argument("--idms-file", help="path to ImageDigestMirrorSet YAML for release-info")
    ap.add_argument("--csaf-dir", type=Path, help="path to offline directory containing CSAF v2 JSON documents")
    ap.add_argument("--csaf-tar", type=Path, help="path to offline CSAF v2 .tar / .tar.gz archive")
    ap.add_argument("--gitops-dir", type=Path, help="path to local clone of redhat-cop gitops-standards repository")
    ap.add_argument("--gitops-repo", help="remote Git URL of redhat-cop gitops-standards repository")
    ap.add_argument("--db-url", help="overrides $DATABASE_URL for this run")
    args, unknown = ap.parse_known_args()

    init_db(args.db_url)

    # Optional Vault / .env pull secret resolution
    pull_secret_data = args.pull_secret or os.environ.get("PULL_SECRET") or os.environ.get("PULL_SECRET_PATH")
    vault_pull_path = args.vault_pull_secret_path or os.environ.get("VAULT_PULL_SECRET_PATH")
    if not pull_secret_data and vault_pull_path and (os.environ.get("VAULT_ADDR") or args.vault_pull_secret_path):
        from vault.client import VaultClient
        vc = VaultClient()
        fetched = vc.get_pull_secret(vault_pull_path)
        if fetched:
            pull_secret_data = fetched
            log.info("Successfully resolved registry pull secret from HashiCorp Vault (%s)", vault_pull_path)


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
                n = module.collect(
                    versions=args.release_version,
                    pull_secret=pull_secret_data,
                    icsp_file=args.icsp_file,
                    idms_file=args.idms_file,
                )
            elif name == "redhat-security":
                n = module.collect(csaf_dir=args.csaf_dir, csaf_tar=args.csaf_tar)
            elif name == "gitops-inventory":
                n = module.collect(gitops_dir=args.gitops_dir, git_repo_url=args.gitops_repo)
            else:
                n = module.collect()
            log.info("--- %s done: %s ---", name, n)
        except Exception:  # noqa: BLE001 - one bad collector shouldn't stop the rest
            log.exception("collector %s failed", name)


if __name__ == "__main__":
    main()

