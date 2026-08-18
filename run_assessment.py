#!/usr/bin/env python3
"""Run a GO / GO-WITH-CAVEATS / NO-GO assessment for one cluster x candidate target.

    python run_assessment.py --cluster east-prod-01 --target 4.22.8
    python run_assessment.py --cluster east-prod-01 --target 4.22.8 --kubeconfig ~/.kube/fleet
    python run_assessment.py --cluster east-prod-01 --target 4.22.8 --llm

With --kubeconfig (or a kubeconfig_context already set on the cluster row),
this attempts a live ClusterVersion read first via collectors.cluster_state,
so conditional-update risk caveats are the CVO's own confirmed-applicable
answer rather than the weaker graph-only "this risk exists on this edge in
general" fallback. Live read failures degrade to that fallback rather than
aborting the assessment.

--llm adds an LLM layer ON TOP of the deterministic result -- it never
replaces it. See llm/ for the guardrails: a narrative summary is validated
against this exact reasons dict before being stored (dropped, not shown, if
it fails validation), and any LLM-proposed extra caveats can only push a `go`
toward `go-with-caveats` -- never touch a blocking reason, never move a
verdict back toward `go`. Point $LLM_BASE_URL at whatever OpenAI-compatible
endpoint you actually have reachable (local vLLM/llama.cpp/Ollama, or a
hosted one) -- see llm/client.py. Without --llm, behavior is unchanged from
before this existed.
"""
from __future__ import annotations

import argparse
import json
import logging

from db.db import get_session, init_db
from db.models import Cluster
from engine.compatibility import assess

log = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description="Run an upgrade compatibility assessment for one cluster")
    ap.add_argument("--cluster", required=True)
    ap.add_argument("--target", required=True, help="candidate OCP version, e.g. 4.22.8")
    ap.add_argument("--kubeconfig", help="attempt a live ClusterVersion read before falling back to DB-only")
    ap.add_argument("--llm", action="store_true", help="add an LLM narrative + optional extra caveats (additive only)")
    ap.add_argument("--llm-base-url", help="overrides $LLM_BASE_URL for this run")
    ap.add_argument("--db-url")
    args = ap.parse_args()

    init_db(args.db_url)

    with get_session() as db:
        cluster = db.query(Cluster).filter_by(name=args.cluster).one_or_none()
        if cluster is None:
            raise SystemExit(f"Cluster {args.cluster!r} not found in inventory")

        live_conditional_updates = None
        if args.kubeconfig or cluster.kubeconfig_context:
            try:
                from collectors.cluster_state import fetch_clusterversion, load_api_clients, parse_clusterversion

                api = load_api_clients(context=cluster.kubeconfig_context, kubeconfig_path=args.kubeconfig)
                live = parse_clusterversion(fetch_clusterversion(api))
                live_conditional_updates = live["conditional_updates"]
                log.info("Live ClusterVersion read OK (%d conditional risks reported)", len(live_conditional_updates))
            except Exception as exc:  # noqa: BLE001 - degrade gracefully, don't abort the assessment
                log.warning("Live read failed (%s); falling back to graph-only risk data", exc)

        # Deterministic verdict -- this is the authoritative result regardless
        # of what happens below.
        row = assess(db, cluster, args.target, live_conditional_updates=live_conditional_updates)

        if args.llm:
            from llm.caveats import apply_additional_caveats, generate_additional_caveats
            from llm.client import LLMConfig
            from llm.narrate import generate_narrative

            config = LLMConfig(base_url=args.llm_base_url)

            if row.verdict != "no-go":
                extra = generate_additional_caveats(
                    cluster.name, cluster.ocp_version, args.target, row.reasons, config=config
                )
                if extra:
                    log.info("LLM proposed %d additional caveat(s)", len(extra))
                    augmented = apply_additional_caveats({"verdict": row.verdict, "reasons": row.reasons}, extra)
                    row.verdict = augmented["verdict"]
                    row.reasons = augmented["reasons"]

            narrative = generate_narrative(cluster.name, cluster.ocp_version, args.target, row.reasons, config=config)
            row.narrative = narrative
            if narrative is None:
                log.info("No LLM narrative attached (endpoint unreachable or failed validation)")

        output = {
            "cluster": cluster.name,
            "target_version": args.target,
            "verdict": row.verdict,
            "reasons": row.reasons,
            "narrative": getattr(row, "narrative", None),
        }

    print(json.dumps(output, indent=2, default=str))


if __name__ == "__main__":
    main()
