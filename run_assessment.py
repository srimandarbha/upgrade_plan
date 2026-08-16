#!/usr/bin/env python3
"""Run a GO / GO-WITH-CAVEATS / NO-GO assessment for one cluster x candidate target version.

Includes:
  - Deterministic facts evaluation (Cincinnati graph, EOL, operators, CVEs)
  - Optional LLM / TestOps Strategic Migration & Escalation Advisor (--llm)
  - Optional TestOps Confluence Policy Ingestion (--confluence)

Examples:
    python run_assessment.py --cluster east-prod-01 --target 4.22.8
    python run_assessment.py --cluster east-prod-01 --target 4.22.8 --llm --confluence
    python run_assessment.py --cluster east-prod-01 --target 5.0.0 --llm
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
    ap.add_argument("--llm", action="store_true", help="enable LLM Strategic Migration & Escalation Advisor")
    ap.add_argument("--confluence", action="store_true", help="ingest TestOps Confluence policies")
    ap.add_argument("--confluence-path", help="path to custom TestOps confluence markdown file")
    ap.add_argument("--kubeconfig", help="path to kubeconfig for live ClusterVersion inspection")
    ap.add_argument("--db-url", help="overrides DATABASE_URL")
    args = ap.parse_args()

    from db.db import get_session, init_db
    from db.models import Advisory, Cluster, ComponentVersion, OperatorCompat
    from engine.compatibility import assess

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
        output = {
            "cluster": cluster.name,
            "current_version": cluster.ocp_version,
            "target_version": args.target,
            "deterministic_verdict": row.verdict.upper(),
            "reasons": row.reasons,
            "evaluated_at": row.evaluated_at.isoformat(),
        }

        strategic_output = None
        if args.llm or args.confluence:
            from engine.llm_advisor import generate_strategic_analysis, load_testops_policy

            installed = (
                db.query(ComponentVersion)
                .filter(ComponentVersion.cluster_id == cluster.id)
                .all()
            )
            compat_records = db.query(OperatorCompat).all()
            cve_count = db.query(Advisory).filter(Advisory.severity == "important").count()
            crit_cve_count = db.query(Advisory).filter(Advisory.severity == "critical").count()
            policy_text = load_testops_policy(args.confluence_path)

            strategic_output = generate_strategic_analysis(
                cluster=cluster,
                target_version=args.target,
                assessment=row,
                installed_components=installed,
                compat_records=compat_records,
                cve_count=cve_count,
                critical_cve_count=crit_cve_count,
                policy_text=policy_text,
            )

    print("\n" + "=" * 70)
    verdict_display = strategic_output["strategic_verdict"] if strategic_output else output["deterministic_verdict"]
    print(f"UPGRADE ASSESSMENT RESULT: {verdict_display}")
    print("=" * 70)

    if strategic_output:
        print("\n--- [EXECUTIVE SYNOPSIS] ---")
        print(strategic_output["executive_synopsis"])

        if strategic_output["escalation_reasons"]:
            print("\n--- [ESCALATION & BLOCKER TRIGGERS] ---")
            for r in strategic_output["escalation_reasons"]:
                print(f" • {r}")

        print("\n--- [DEEP COMPONENT & STORAGE IMPACT] ---")
        for k, v in strategic_output["impact_analysis"].items():
            if k != "version_drift_index":
                print(f" • {k.upper()}: {v}")

        print("\n--- [TESTOPS REMEDIATION & QUALIFICATION PLAN] ---")
        for step in strategic_output["testops_remediation_plan"]:
            print(f" Step {step['step']} [{step['phase']}]:")
            print(f"   Action: {step['action']}")
            print(f"   Gate:   {step['gate']}")

        print("\n--- [HUMAN-IN-THE-LOOP SIGN-OFF GATE] ---")
        print(f" Status: {strategic_output['human_in_the_loop_sign_off']['status']}")
        print(f" Required Approvers: {', '.join(strategic_output['human_in_the_loop_sign_off']['required_approvers'])}")
        print(" Checklist:")
        for item in strategic_output["human_in_the_loop_sign_off"]["sign_off_checklist"]:
            print(f"   {item}")

    print("\n--- [RAW AUDIT JSON PAYLOAD] ---")
    print(json.dumps(strategic_output or output, indent=2, default=str))


if __name__ == "__main__":
    main()
