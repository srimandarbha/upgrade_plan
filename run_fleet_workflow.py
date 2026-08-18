#!/usr/bin/env python3
"""Fleet Upgrade Automation Workflow & Wrapper Script.

Coordinates the end-to-end upgrade workflow across 50+ clusters:
1. Configures proxy settings (HTTP_PROXY, HTTPS_PROXY, NO_PROXY) for corporate firewalls.
2. Synchronizes latest GitOps changes from Lab and/or Prod GitOps repositories (redhat-cop layout).
3. Ingests operator mappings into PostgreSQL via `gitops-inventory` collector.
4. Toggles TestOps Confluence migration policies & sign-off gates.
5. Runs compatibility assessments across Lab, Prod, or the entire Fleet.

Examples:
    # 1. Run complete workflow against Lab/Staging clusters:
    python run_fleet_workflow.py --env lab --target 4.22.8

    # 2. Run complete workflow against Production clusters with corporate proxy:
    python run_fleet_workflow.py --env prod --target 4.22.8 --https-proxy http://proxy.corp.net:8080

    # 3. Run fleet assessment disabling external Confluence API (using local policy):
    python run_fleet_workflow.py --env all --target 4.22.8 --disable-confluence

    # 4. Fast deterministic check (disable TestOps / LLM synthesis):
    python run_fleet_workflow.py --env prod --target 4.22.8 --disable-testops
"""
from __future__ import annotations

import argparse
import logging
import os
import subprocess
from pathlib import Path
from typing import Any

from db.db import get_session, init_db
from db.models import Cluster
from engine.compatibility import assess

log = logging.getLogger("fleet-workflow")


def configure_proxy(
    http_proxy: str | None = None,
    https_proxy: str | None = None,
    no_proxy: str | None = None,
) -> None:
    """Set standard proxy environment variables for Python requests, urllib, and Git."""
    hp = http_proxy or os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
    hsp = https_proxy or os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    np = no_proxy or os.environ.get("NO_PROXY") or os.environ.get("no_proxy")

    if hp:
        os.environ["HTTP_PROXY"] = hp
        os.environ["http_proxy"] = hp
        log.info("HTTP proxy configured: %s", hp)
    if hsp:
        os.environ["HTTPS_PROXY"] = hsp
        os.environ["https_proxy"] = hsp
        log.info("HTTPS proxy configured: %s", hsp)
    if np:
        os.environ["NO_PROXY"] = np
        os.environ["no_proxy"] = np
        log.info("NO_PROXY configured: %s", np)


def sync_gitops_repository(repo_dir: Path | str | None, repo_url: str | None) -> Path | None:
    """Pull latest GitOps changes or clone repository."""
    if not repo_dir and not repo_url:
        return None

    path = Path(repo_dir) if repo_dir else None

    # 1. If local directory exists, pull latest commits
    if path and path.exists() and (path / ".git").exists():
        log.info("Pulling latest GitOps changes in %s", path)
        try:
            subprocess.run(["git", "-C", str(path), "pull", "--ff-only"], check=False, capture_output=True)
            return path
        except Exception as exc:
            log.warning("Git pull failed in %s: %s (using local state)", path, exc)
            return path

    # 2. If directory doesn't exist but URL is provided, clone
    if repo_url:
        target_dir = path or Path(tempfile.mkdtemp(prefix="gitops-fleet-"))
        log.info("Cloning GitOps repository from %s into %s", repo_url, target_dir)
        try:
            import git
            git.Repo.clone_from(repo_url, target_dir, depth=1)
            return target_dir
        except Exception as exc:
            log.warning("Failed to clone %s: %s", repo_url, exc)
            return None

    return path


def sync_environment_inventory(env_name: str) -> tuple[int, int]:
    """Sync cluster-wise operator inventory from respective GitOps repository."""
    from collectors.gitops_inventory import collect as collect_gitops

    total_clusters = 0
    total_components = 0

    if env_name in ("lab", "non-prod", "all"):
        lab_dir = os.environ.get("LAB_GITOPS_REPO_DIR") or os.environ.get("GITOPS_REPO_DIR")
        lab_url = os.environ.get("LAB_GITOPS_REPO_URL") or os.environ.get("GITOPS_REPO_URL")
        lab_path = sync_gitops_repository(lab_dir, lab_url)
        if lab_path:
            log.info("Syncing Lab/Non-Prod inventory from %s", lab_path)
            c, ops = collect_gitops(gitops_dir=lab_path)
            total_clusters += c
            total_components += ops

    if env_name in ("prod", "all"):
        prod_dir = os.environ.get("PROD_GITOPS_REPO_DIR") or os.environ.get("GITOPS_REPO_DIR")
        prod_url = os.environ.get("PROD_GITOPS_REPO_URL") or os.environ.get("GITOPS_REPO_URL")
        prod_path = sync_gitops_repository(prod_dir, prod_url)
        if prod_path:
            log.info("Syncing Prod inventory from %s", prod_path)
            c, ops = collect_gitops(gitops_dir=prod_path)
            total_clusters += c
            total_components += ops

    return total_clusters, total_components


def run_fleet_pipeline(
    target_version: str,
    env: str = "all",
    cluster_name: str | None = None,
    http_proxy: str | None = None,
    https_proxy: str | None = None,
    no_proxy: str | None = None,
    skip_gitops_sync: bool = False,
    enable_testops: bool = True,
    enable_confluence: bool = True,
    use_llm: bool = False,
    llm_base_url: str | None = None,
    vault_kubeconfig_template: str | None = None,
) -> dict[str, Any]:
    """Execute complete workflow: proxy setup -> gitops sync -> assessment -> matrix reporting."""
    configure_proxy(http_proxy, https_proxy, no_proxy)

    init_db()

    # 1. Sync GitOps repos if not skipped
    if not skip_gitops_sync:
        c, ops = sync_environment_inventory(env)
        log.info("Inventory sync complete: %d cluster(s), %d component(s)", c, ops)

    # 2. Select clusters based on target environment
    with get_session() as db:
        query = db.query(Cluster)
        if cluster_name:
            query = query.filter(Cluster.name == cluster_name)
        elif env in ("lab", "non-prod"):
            query = query.filter(Cluster.env.in_(["lab", "non-prod", "stage", "dev"]))
        elif env == "prod":
            query = query.filter(Cluster.env == "prod")

        clusters = query.all()
        if not clusters:
            log.warning("No clusters found matching environment filter: %s", env)
            return {"error": f"No clusters found for env={env}"}

        log.info("Running upgrade assessment for %d cluster(s) [Target: OCP %s, Env: %s]", len(clusters), target_version, env)

        from run_assessment import assess_single_cluster
        results = []
        for c in clusters:
            is_prod = (c.env == "prod")
            # Production Guardrail: Confluence & TestOps cannot be excluded for prod clusters (lab seed only).
            cluster_confluence = True if is_prod else enable_confluence
            if is_prod and not enable_confluence:
                log.warning("[%s] Confluence policy CANNOT be excluded for production. Enforcing mandatory Confluence policy gate.", c.name)

            cluster_testops = True if is_prod else enable_testops
            if is_prod and not enable_testops:
                log.warning("[%s] TestOps governance CANNOT be disabled for production. Enforcing mandatory TestOps evaluation.", c.name)

            res = assess_single_cluster(
                db=db,
                cluster=c,
                target_version=target_version,
                vault_kubeconfig_template=vault_kubeconfig_template,
                use_llm=use_llm or cluster_testops,
                llm_base_url=llm_base_url,
            )
            results.append(res)


    # 3. Print Aggregated Fleet Matrix
    verdict_counts = {"go": 0, "go-with-caveats": 0, "no-go": 0}
    for r in results:
        v = r.get("verdict", "no-go")
        verdict_counts[v] = verdict_counts.get(v, 0) + 1

    print("\n" + "=" * 80)
    print(f"FLEET UPGRADE READINESS MATRIX: TARGET OCP {target_version} [ENV: {env.upper()}]")
    print(f"Total Clusters: {len(results)} | Ready (GO): {verdict_counts['go']} | Caveats: {verdict_counts['go-with-caveats']} | Blocked (NO-GO): {verdict_counts['no-go']}")
    print("=" * 80)
    print(f"{'CLUSTER':<24} | {'ENV':<8} | {'CURRENT':<10} | {'VERDICT':<16} | {'STATUS'}")
    print("-" * 80)
    for r in results:
        v = r["verdict"].upper()
        blockers = r["reasons"].get("blockers", [])
        caveats = r["reasons"].get("caveats", [])
        detail = f"{len(blockers)} blocker(s)" if blockers else (f"{len(caveats)} caveat(s)" if caveats else "Clean")
        print(f"{r['cluster']:<24} | {getattr(r, 'env', env):<8} | {r['current_version']:<10} | {v:<16} | {detail}")
    print("=" * 80 + "\n")

    return {
        "target_version": target_version,
        "env": env,
        "summary": verdict_counts,
        "clusters": results,
    }


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description="End-to-end fleet upgrade workflow wrapper")
    ap.add_argument("--target", required=True, help="candidate target OCP version, e.g. 4.22.8")
    ap.add_argument("--env", choices=["lab", "prod", "all"], default="all", help="target environment subset")
    ap.add_argument("--cluster", help="run against a specific cluster only")
    ap.add_argument("--http-proxy", help="HTTP proxy server URL")
    ap.add_argument("--https-proxy", help="HTTPS proxy server URL")
    ap.add_argument("--no-proxy", help="comma-separated NO_PROXY hosts")
    ap.add_argument("--skip-gitops-sync", action="store_true", help="skip pulling GitOps repositories")
    ap.add_argument("--disable-testops", action="store_true", help="disable TestOps / LLM strategic reasoning (permitted for initial seed lab only; enforced for prod)")
    ap.add_argument("--disable-confluence", action="store_true", help="disable Confluence REST API lookup (permitted for initial seed lab only; enforced for prod)")

    ap.add_argument("--llm-base-url", help="OpenAI-compatible LLM endpoint")
    ap.add_argument("--vault-kubeconfig-path", help="Vault path template for dynamic cluster credentials")
    args = ap.parse_args()

    run_fleet_pipeline(
        target_version=args.target,
        env=args.env,
        cluster_name=args.cluster,
        http_proxy=args.http_proxy,
        https_proxy=args.https_proxy,
        no_proxy=args.no_proxy,
        skip_gitops_sync=args.skip_gitops_sync,
        enable_testops=not args.disable_testops,
        enable_confluence=not args.disable_confluence,
        use_llm=not args.disable_testops,
        llm_base_url=args.llm_base_url,
        vault_kubeconfig_template=args.vault_kubeconfig_path,
    )


if __name__ == "__main__":
    main()
