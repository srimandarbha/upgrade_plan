#!/usr/bin/env python3
"""Run a GO / GO-WITH-CAVEATS / NO-GO assessment for single clusters or an entire 50+ cluster fleet.

Examples:
    # 1. Assess a single cluster:
    python run_assessment.py --cluster east-prod-01 --target 4.22.8

    # 2. Assess entire 50+ cluster fleet in PostgreSQL:
    python run_assessment.py --all --target 4.22.8

    # 3. Dynamic cluster login via HashiCorp Vault:
    python run_assessment.py --cluster east-prod-01 --target 4.22.8 --vault-kubeconfig-path secret/data/clusters/{cluster}

    # 4. With live cluster inspection and LLM synthesis:
    python run_assessment.py --cluster east-prod-01 --target 4.22.8 --kubeconfig ~/.kube/fleet --llm
"""
from __future__ import annotations

import argparse
import json
import logging
import tempfile
from typing import Any

from db.db import get_session, init_db
from db.models import Cluster
from engine.compatibility import assess

log = logging.getLogger(__name__)


def assess_single_cluster(
    db: Any,
    cluster: Cluster,
    target_version: str,
    kubeconfig_path: str | None = None,
    vault_kubeconfig_template: str | None = None,
    use_llm: bool = False,
    llm_base_url: str | None = None,
) -> dict[str, Any]:
    """Run assessment for one cluster record."""
    resolved_kubeconfig = kubeconfig_path

    # Dynamic Vault Kubeconfig retrieval if configured
    if vault_kubeconfig_template and not resolved_kubeconfig:
        try:
            from vault.client import VaultClient
            vc = VaultClient()
            k_content = vc.get_cluster_kubeconfig(cluster.name, template=vault_kubeconfig_template)
            if k_content:
                tmp_k = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
                tmp_k.write(k_content)
                tmp_k.close()
                resolved_kubeconfig = tmp_k.name
        except Exception as exc:
            log.warning("Vault kubeconfig fetch failed for %s: %s", cluster.name, exc)

    live_conditional_updates = None
    if resolved_kubeconfig or cluster.kubeconfig_context:
        try:
            from collectors.cluster_state import fetch_clusterversion, load_api_clients, parse_clusterversion

            api = load_api_clients(context=cluster.kubeconfig_context, kubeconfig_path=resolved_kubeconfig)
            live = parse_clusterversion(fetch_clusterversion(api))
            live_conditional_updates = live["conditional_updates"]
            log.info("[%s] Live ClusterVersion read OK (%d conditional risks)", cluster.name, len(live_conditional_updates))
        except Exception as exc:  # noqa: BLE001 - degrade gracefully
            log.warning("[%s] Live read failed (%s); falling back to graph risk data", cluster.name, exc)

    # Clean up temp Vault kubeconfig if created
    if vault_kubeconfig_template and resolved_kubeconfig and resolved_kubeconfig != kubeconfig_path:
        try:
            import os
            os.remove(resolved_kubeconfig)
        except OSError:
            pass

    row = assess(db, cluster, target_version, live_conditional_updates=live_conditional_updates)

    narrative = None
    if use_llm:
        from engine.llm_advisor import generate_expert_decision, load_testops_policy
        from db.models import ComponentVersion, OperatorCompat, Advisory

        comps = db.query(ComponentVersion).filter_by(cluster_id=cluster.id).all()
        compats = db.query(OperatorCompat).all()
        cve_count = db.query(Advisory).filter(Advisory.source == "redhat-cve").count()
        crit_count = db.query(Advisory).filter(Advisory.severity == "critical").count()
        policy = load_testops_policy()

        strat = generate_expert_decision(
            cluster=cluster,
            target_version=target_version,
            assessment=row,
            installed_components=comps,
            compat_records=compats,
            cve_count=cve_count,
            critical_cve_count=crit_count,
            policy_text=policy,
        )
        narrative = strat.get("executive_synopsis")
        row.narrative = narrative

    return {
        "cluster": cluster.name,
        "current_version": cluster.ocp_version,
        "target_version": target_version,
        "verdict": row.verdict,
        "reasons": row.reasons,
        "narrative": narrative or getattr(row, "narrative", None),
    }



def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description="Run upgrade compatibility assessment for clusters in inventory")
    ap.add_argument("--cluster", help="cluster name from inventory (e.g. east-prod-01)")
    ap.add_argument("--all", "--fleet", action="store_true", help="evaluate all 50+ clusters in inventory across fleet")
    ap.add_argument("--target", required=True, help="candidate OCP version, e.g. 4.22.8")
    ap.add_argument("--kubeconfig", help="path to kubeconfig for live ClusterVersion inspection")
    ap.add_argument("--vault-kubeconfig-path", help="Vault path template for dynamic cluster credentials (e.g. secret/data/clusters/{cluster})")
    ap.add_argument("--llm", action="store_true", help="add an LLM narrative + optional extra caveats (additive only)")
    ap.add_argument("--llm-base-url", help="overrides $LLM_BASE_URL for this run")
    ap.add_argument("--json", action="store_true", help="output strictly raw JSON")
    ap.add_argument("--db-url")
    args = ap.parse_args()

    if not args.cluster and not args.all:
        ap.error("Specify either --cluster <name> or --all to evaluate the fleet.")

    init_db(args.db_url)

    with get_session() as db:
        if args.all:
            clusters = db.query(Cluster).all()
            if not clusters:
                raise SystemExit("No clusters found in PostgreSQL inventory. Run collectors.gitops_inventory or cluster_state first.")
            log.info("Running fleet upgrade assessment across %d clusters for target %s", len(clusters), args.target)
        else:
            cluster = db.query(Cluster).filter_by(name=args.cluster).one_or_none()
            if cluster is None:
                raise SystemExit(f"Cluster {args.cluster!r} not found in inventory")
            clusters = [cluster]

        results = []
        for c in clusters:
            res = assess_single_cluster(
                db=db,
                cluster=c,
                target_version=args.target,
                kubeconfig_path=args.kubeconfig,
                vault_kubeconfig_template=args.vault_kubeconfig_path,
                use_llm=args.llm,
                llm_base_url=args.llm_base_url,
            )
            results.append(res)

    if not args.all and len(results) == 1:
        print(json.dumps(results[0], indent=2, default=str))
        return

    # Fleet-wide aggregated summary
    verdict_counts = {"go": 0, "go-with-caveats": 0, "no-go": 0}
    for r in results:
        v = r.get("verdict", "no-go")
        verdict_counts[v] = verdict_counts.get(v, 0) + 1

    fleet_payload = {
        "fleet_size": len(results),
        "target_version": args.target,
        "summary": verdict_counts,
        "clusters": results,
    }

    if args.json:
        print(json.dumps(fleet_payload, indent=2, default=str))
        return

    # Formatted Fleet Dashboard
    print("\n" + "=" * 78)
    print(f"FLEET UPGRADE READINESS MATRIX: TARGET OCP {args.target}")
    print(f"Total Clusters: {len(results)} | Ready (GO): {verdict_counts['go']} | Caveats: {verdict_counts['go-with-caveats']} | Blocked (NO-GO): {verdict_counts['no-go']}")
    print("=" * 78)
    print(f"{'CLUSTER':<24} | {'CURRENT':<10} | {'VERDICT':<16} | {'BLOCKERS / CAVEATS'}")
    print("-" * 78)
    for r in results:
        v = r["verdict"].upper()
        blockers = r["reasons"].get("blockers", [])
        caveats = r["reasons"].get("caveats", [])
        detail = f"{len(blockers)} blocker(s)" if blockers else (f"{len(caveats)} caveat(s)" if caveats else "Clean")
        print(f"{r['cluster']:<24} | {r['current_version']:<10} | {v:<16} | {detail}")
    print("=" * 78 + "\n")


if __name__ == "__main__":
    main()

