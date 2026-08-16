#!/usr/bin/env python3
"""Run an automated upgrade assessment for one cluster x candidate target version.

Unified Assessment Engine:
  - Default: Deterministic evaluation (fast, 100% rule-based facts check)
  - With --llm: LLM-driven decision & reasoning (via local/remote LLM endpoint)

Both modes output the exact same JSON decision schema.

Examples:
    # 1. Deterministic Mode (Default):
    python run_assessment.py --cluster east-prod-01 --target 4.22.8

    # 2. LLM Mode (Local LLM thinking):
    python run_assessment.py --cluster east-prod-01 --target 4.22.8 --llm

    # 3. Pure JSON Output (for CI/CD pipelines & GitOps bots):
    python run_assessment.py --cluster east-prod-01 --target 4.22.8 --json
"""
from __future__ import annotations

import argparse
import json
import logging

log = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(
        description="Run an automated GO / GO-WITH-CAVEATS / NO-GO upgrade compatibility assessment."
    )
    ap.add_argument("--cluster", required=True, help="cluster name from inventory (e.g. east-prod-01)")
    ap.add_argument("--target", required=True, help="candidate target OCP version (e.g. 4.22.8 or 5.0.0)")
    ap.add_argument("--llm", action="store_true", help="use LLM for decision reasoning and analysis (default: deterministic)")
    ap.add_argument("--llm-url", default="http://127.0.0.1:8080/v1/chat/completions", help="local or remote LLM endpoint URL")
    ap.add_argument("--json", action="store_true", help="output strictly raw JSON (ideal for GitOps bots & scripts)")
    ap.add_argument("--confluence-page-id", help="placeholder: Confluence Page ID for API ingestion")
    ap.add_argument("--confluence-url", help="placeholder: Confluence Base URL")
    ap.add_argument("--kubeconfig", help="path to kubeconfig for live ClusterVersion inspection")
    ap.add_argument("--db-url", help="overrides DATABASE_URL")
    args = ap.parse_args()

    from db.db import get_session, init_db
    from db.models import Advisory, Cluster, ComponentVersion, OperatorCompat
    from engine.compatibility import assess
    from engine.llm_advisor import generate_strategic_analysis, load_testops_policy

    init_db(args.db_url)

    with get_session() as db:
        cluster = db.query(Cluster).filter_by(name=args.cluster).one_or_none()
        if cluster is None:
            raise SystemExit(
                f"Cluster {args.cluster!r} not found in inventory. "
                "Add it to the 'clusters' table first or run collectors.cluster_state."
            )

        live_conditional_updates = None
        if args.kubeconfig or cluster.kubeconfig_context:
            try:
                from collectors.cluster_state import fetch_clusterversion, load_api_clients, parse_clusterversion

                api = load_api_clients(context=cluster.kubeconfig_context, kubeconfig_path=args.kubeconfig)
                live = parse_clusterversion(fetch_clusterversion(api))
                live_conditional_updates = live["conditional_updates"]
                log.info("Live ClusterVersion read OK (%d conditional risks reported)", len(live_conditional_updates))
            except Exception as exc:  # noqa: BLE001 - degrade gracefully, don't abort
                log.warning("Live read failed (%s); falling back to database graph risk data", exc)

        row = assess(db, cluster, args.target, live_conditional_updates=live_conditional_updates)

        installed = (
            db.query(ComponentVersion)
            .filter(ComponentVersion.cluster_id == cluster.id)
            .all()
        )
        compat_records = db.query(OperatorCompat).all()
        cve_count = db.query(Advisory).filter(Advisory.severity == "important").count()
        crit_cve_count = db.query(Advisory).filter(Advisory.severity == "critical").count()
        policy_text = load_testops_policy()

        decision_payload = generate_strategic_analysis(
            cluster=cluster,
            target_version=args.target,
            assessment=row,
            installed_components=installed,
            compat_records=compat_records,
            cve_count=cve_count,
            critical_cve_count=crit_cve_count,
            policy_text=policy_text,
            llm_url=args.llm_url,
            use_live_llm=args.llm,
        )

    if args.json:
        print(json.dumps(decision_payload, indent=2, default=str))
        return

    print("\n" + "=" * 70)
    print(f"UPGRADE ASSESSMENT RESULT: {decision_payload['verdict']} [Mode: {decision_payload['evaluation_mode'].upper()}]")
    print("=" * 70)

    print("\n--- [EXECUTIVE SYNOPSIS] ---")
    print(decision_payload["executive_synopsis"])

    blockers = decision_payload["reasons"].get("blockers", [])
    if blockers:
        print("\n--- [ESCALATION & BLOCKER TRIGGERS] ---")
        for r in blockers:
            print(f" • {r}")

    print("\n--- [DEEP COMPONENT & STORAGE IMPACT] ---")
    for k, v in decision_payload["impact_analysis"].items():
        if k != "version_drift":
            print(f" • {k.replace('_', ' ').upper()}: {v}")

    print("\n--- [TESTOPS REMEDIATION & QUALIFICATION PLAN] ---")
    for step in decision_payload["testops_remediation_plan"]:
        print(f" Step {step['step']} [{step['phase']}]:")
        print(f"   Action: {step['action']}")
        print(f"   Gate:   {step['gate']}")

    print("\n--- [HUMAN-IN-THE-LOOP SIGN-OFF GATE] ---")
    print(f" Status: {decision_payload['human_in_the_loop_sign_off']['status']}")
    print(f" Required Approvers: {', '.join(decision_payload['human_in_the_loop_sign_off']['required_approvers'])}")
    print(" Checklist:")
    for item in decision_payload["human_in_the_loop_sign_off"]["sign_off_checklist"]:
        print(f"   {item}")

    print("\n--- [UNIFIED DECISION JSON PAYLOAD] ---")
    print(json.dumps(decision_payload, indent=2, default=str))


if __name__ == "__main__":
    main()
