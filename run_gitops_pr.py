#!/usr/bin/env python3
"""Open (or update) a GitOps PR bumping a cluster's OCP target version, gated
on the most recent stored assessment for that cluster x target.

    python run_gitops_pr.py --cluster east-prod-01 --target 4.22.8 --dry-run
    python run_gitops_pr.py --cluster east-prod-01 --target 4.22.8

Refuses outright on a no-go verdict -- prints the blocking reasons and exits
nonzero, no git/GitHub calls made. A go-with-caveats verdict opens the PR as
a draft by default; pass --force-ready to open it ready-for-review anyway
(the caveats still show up in the PR body either way). Re-running against an
existing branch/PR updates it in place rather than creating a duplicate.

Reads per-cluster repo config from data/gitops_targets.yaml (override with
--targets-file) and the GitHub token from $GITHUB_TOKEN (not required for
--dry-run, which stops before any git push or GitHub API call).
"""
from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path

import git
import requests
import yaml

from db.db import get_session, init_db
from db.models import Assessment, Cluster
from gitops.bot import RepoTarget, open_or_update_pr

log = logging.getLogger(__name__)

DEFAULT_TARGETS_PATH = Path(__file__).resolve().parent / "data" / "gitops_targets.yaml"
REQUIRED_TARGET_KEYS = ["repo_url", "owner", "repo_name", "cluster_path", "curator_namespace"]


def load_target(cluster_name: str, path: Path = DEFAULT_TARGETS_PATH) -> RepoTarget:
    with open(path, "r", encoding="utf-8") as fh:
        config = yaml.safe_load(fh) or {}
    entry = (config.get("clusters") or {}).get(cluster_name)
    if entry is None:
        raise SystemExit(
            f"No GitOps repo config for cluster {cluster_name!r} in {path}. "
            f"Add an entry under clusters:{cluster_name}: first."
        )
    merged = {**config.get("defaults", {}), **entry}
    missing = [k for k in REQUIRED_TARGET_KEYS if k not in merged]
    if missing:
        raise SystemExit(f"{path} entry for {cluster_name!r} is missing required keys: {missing}")
    return RepoTarget(
        repo_url=merged["repo_url"],
        owner=merged["owner"],
        repo_name=merged["repo_name"],
        cluster_path=merged["cluster_path"],
        curator_namespace=merged["curator_namespace"],
        base_branch=merged.get("base_branch", "main"),
        upstream_graph_url=merged.get("upstream_graph_url"),
    )


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description="Open/update a GitOps PR for a cluster's OCP upgrade")
    ap.add_argument("--cluster", required=True, help="cluster name from inventory (e.g. east-prod-01)")
    ap.add_argument("--target", required=True, help="candidate target OCP version (e.g. 4.22.8)")
    ap.add_argument("--targets-file", type=Path, default=DEFAULT_TARGETS_PATH, help="path to gitops_targets.yaml")
    ap.add_argument("--force-ready", action="store_true", help="open ready-for-review even on go-with-caveats")
    ap.add_argument("--dry-run", action="store_true", help="render everything; skip git push + GitHub API calls")
    ap.add_argument("--db-url", help="overrides DATABASE_URL")
    args = ap.parse_args()

    init_db(args.db_url)
    target = load_target(args.cluster, args.targets_file)

    token = os.environ.get("GITHUB_TOKEN")
    if not token and not args.dry_run:
        raise SystemExit("GITHUB_TOKEN is not set (or pass --dry-run to preview without it)")

    with get_session() as db:
        cluster = db.query(Cluster).filter_by(name=args.cluster).one_or_none()
        if cluster is None:
            raise SystemExit(f"Cluster {args.cluster!r} not found in inventory")

        assessment = (
            db.query(Assessment)
            .filter_by(cluster_id=cluster.id, target_version=args.target)
            .order_by(Assessment.evaluated_at.desc())
            .first()
        )
        if assessment is None:
            raise SystemExit(
                f"No assessment on file for {args.cluster} -> {args.target}. Run first:\n"
                f"  python run_assessment.py --cluster {args.cluster} --target {args.target}"
            )
        if assessment.verdict == "no-go":
            log.error("Verdict is NO-GO for %s -> %s -- refusing to open a PR.", args.cluster, args.target)
            reasons = assessment.reasons or {}
            for b in (reasons.get("blockers") or reasons.get("blocking") or []):
                detail = b.get("detail", b) if isinstance(b, dict) else b
                kind = b.get("kind") if isinstance(b, dict) else "Blocker"
                log.error("  blocking: %s: %s", kind, detail)
            raise SystemExit(1)

        try:
            result = open_or_update_pr(
                cluster_name=cluster.name,
                current_version=cluster.ocp_version,
                target_version=args.target,
                verdict=assessment.verdict,
                reasons=assessment.reasons or {},
                target=target,
                token=token or "dry-run-no-token-needed",
                assessment_id=assessment.id,
                evaluated_at=str(assessment.evaluated_at),
                force_ready=args.force_ready,
                dry_run=args.dry_run,
            )
        except requests.exceptions.HTTPError as exc:
            resp = exc.response
            raise SystemExit(
                f"GitHub API call failed: {resp.status_code} {resp.reason} for {resp.url}\n"
                f"The branch/commit was still pushed to {target.repo_url} -- fix the auth issue "
                f"(check $GITHUB_TOKEN's scopes) and re-run; it'll pick up the existing branch."
            ) from exc
        except git.exc.GitCommandError as exc:
            raise SystemExit(f"git operation failed: {exc}") from exc

    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
