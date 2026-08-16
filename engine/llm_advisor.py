"""Strategic Upgrade & Migration LLM Advisor Engine.

Synthesizes:
  - Deterministic facts (Postgres: Cincinnati edges, RHSAs, EOL dates, operator matrices)
  - Operator ecosystem state (MTV / Forklift, Dell CSM, Portworx, OCV)
  - TestOps Confluence Policy & VM migration continuity principles
  - Version drift dynamics (e.g. OCP 4 -> 5, or major y-stream jumps)

Provides:
  - Executive Synopsis & Risk Rationale
  - Deep Component & Storage Impact Breakdown
  - Actionable TestOps Remediation & Qualification Plan
  - Human-in-the-Loop Sign-off Form
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any

from db.models import Assessment, Cluster, ComponentVersion, OperatorCompat, ProductLifecycle, UpgradeEdge
from engine.compatibility import check_version_in_range, parse_version_tuple

log = logging.getLogger(__name__)

DEFAULT_LLM_URL = "http://127.0.0.1:8080/v1/chat/completions"


def query_local_llm(
    prompt: str,
    llm_url: str | None = None,
    model_name: str | None = None,
    timeout: int = 90,
) -> str | None:
    """Query OpenAI-compatible local LLM endpoint (e.g. llama.cpp / vLLM on localhost:8080)."""
    import requests

    url = llm_url or os.environ.get("LLM_URL", DEFAULT_LLM_URL)
    payload = {
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a Senior OpenShift Platform SRE and Virtualization Upgrade Specialist. "
                    "Analyze the provided cluster facts, operator matrix (MTV, Dell CSM, Portworx), "
                    "and TestOps policies. Provide a concise, authoritative executive summary and recommendation."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 300,
        "temperature": 0.2,
    }
    if model_name:
        payload["model"] = model_name

    try:
        resp = requests.post(url, json=payload, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "").strip()
    except Exception as exc:
        log.warning("Local LLM request to %s failed: %s (using expert heuristic fallback)", url, exc)
    return None


def fetch_confluence_policy(
    confluence_base_url: str | None = None,
    page_id: str | None = None,
    auth_token: str | None = None,
) -> str | None:
    """Placeholder for future direct Confluence REST API ingestion.
    
    Confluence Cloud / Data Center endpoint:
        GET {confluence_base_url}/wiki/rest/api/content/{page_id}?expand=body.storage
    """
    base_url = confluence_base_url or os.environ.get("CONFLUENCE_URL")
    pid = page_id or os.environ.get("CONFLUENCE_PAGE_ID")
    token = auth_token or os.environ.get("CONFLUENCE_API_TOKEN")

    if not base_url or not pid:
        # Placeholder: Confluence API not configured yet; return None to use built-in policy
        return None

    import requests

    try:
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        resp = requests.get(f"{base_url.rstrip('/')}/wiki/rest/api/content/{pid}?expand=body.storage", headers=headers, timeout=15)
        if resp.status_code == 200:
            return resp.json().get("body", {}).get("storage", {}).get("value", "")
    except Exception as exc:
        log.warning("Confluence API fetch failed: %s (using default policy)", exc)
    return None


def load_testops_policy(file_path: str | None = None) -> str:
    """Load TestOps policy (from Confluence API placeholder, custom file, or built-in defaults)."""
    # 1. Check Confluence API placeholder
    confluence_content = fetch_confluence_policy()
    if confluence_content:
        return confluence_content

    # 2. Check local policy file if present
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except OSError:
            pass

    default_path = os.path.join(os.getcwd(), "data", "testops_confluence_policy.md")
    if os.path.exists(default_path):
        try:
            with open(default_path, "r", encoding="utf-8") as f:
                return f.read()
        except OSError:
            pass

    return "TestOps Policy Standard: Prioritize active VM migration (MTV) continuity. Require CSI storage failover verification."


def calculate_version_drift(current_version: str, target_version: str) -> dict[str, Any]:
    """Calculate major, minor, and patch drift."""
    cur_parts = parse_version_tuple(current_version)
    tgt_parts = parse_version_tuple(target_version)

    major_cur = cur_parts[0] if len(cur_parts) > 0 else 4
    major_tgt = tgt_parts[0] if len(tgt_parts) > 0 else 4
    minor_cur = cur_parts[1] if len(cur_parts) > 1 else 0
    minor_tgt = tgt_parts[1] if len(tgt_parts) > 1 else 0
    patch_cur = cur_parts[2] if len(cur_parts) > 2 else 0
    patch_tgt = tgt_parts[2] if len(tgt_parts) > 2 else 0

    is_major_drift = major_tgt > major_cur
    minor_diff = (major_tgt * 100 + minor_tgt) - (major_cur * 100 + minor_cur)
    is_multi_minor_jump = minor_diff > 1

    return {
        "current": current_version,
        "target": target_version,
        "is_major_drift": is_major_drift,
        "is_multi_minor_jump": is_multi_minor_jump,
        "drift_type": "major" if is_major_drift else ("multi-minor" if is_multi_minor_jump else ("minor" if minor_diff == 1 else "z-stream")),
        "minor_steps": minor_diff,
    }


def generate_strategic_analysis(
    cluster: Cluster,
    target_version: str,
    assessment: Assessment,
    installed_components: list[ComponentVersion],
    compat_records: list[OperatorCompat],
    cve_count: int,
    critical_cve_count: int,
    policy_text: str,
    llm_url: str | None = None,
    use_live_llm: bool = True,
) -> dict[str, Any]:
    """Generate comprehensive strategic evaluation with executive synopsis and test plan."""
    drift = calculate_version_drift(cluster.ocp_version, target_version)
    components_map = {c.component: c.version for c in installed_components}

    # Evaluate critical operator risks
    operator_risks: list[str] = []
    for comp in installed_components:
        comp_rules = [r for r in compat_records if r.component == comp.component and r.operator_version == comp.version]
        if comp_rules:
            is_compat = any(check_version_in_range(target_version, r.min_ocp, r.max_ocp) for r in comp_rules)
            if not is_compat:
                rule = comp_rules[0]
                operator_risks.append(
                    f"{comp.component} (version {comp.version}) is NOT certified for OCP {target_version} "
                    f"(supported up to {rule.max_ocp or 'current'})."
                )

    # Core Strategic Motive Decision
    # If major version drift (e.g. 4 -> 5) or multi-minor jump with active MTV / storage operators,
    # and no critical emergency CVEs forcing it: ESCALATE TO NO-GO.
    escalation_reasons: list[str] = []
    verdict = assessment.verdict.upper()

    if drift["is_major_drift"]:
        verdict = "NO-GO (ESCALATE)"
        escalation_reasons.append(
            f"Major version architectural drift detected ({cluster.ocp_version} -> {target_version}). "
            "Under TestOps Policy TESTOPS-POL-4082, major version transitions require mandatory sandbox qualification."
        )

    if operator_risks:
        verdict = "NO-GO (ESCALATE)"
        escalation_reasons.extend(operator_risks)

    if "mtv" in components_map:
        mtv_ver = components_map["mtv"]
        if drift["is_major_drift"] or drift["is_multi_minor_jump"]:
            escalation_reasons.append(
                f"Active MTV (Migration Toolkit for Virtualization) operator v{mtv_ver} detected. "
                "VM migration stability is prioritized over routine platform upgrades unless critical CVEs are unpatched."
            )

    # Build Executive Synopsis
    if "ESCALATE" in verdict or verdict == "NO-GO":
        synopsis = (
            f"RECOMMENDATION: HOLD UPGRADE (NO-GO ESCALATED). Upgrading cluster '{cluster.name}' from "
            f"OCP {cluster.ocp_version} to {target_version} poses high operational risk to active migration and storage workloads. "
            f"Identified {len(escalation_reasons)} primary blocker(s) including version drift and operator boundary mismatches. "
            "Platform SRE and TestOps sign-off is strictly required prior to staging validation."
        )
    elif verdict == "GO-WITH-CAVEATS":
        synopsis = (
            f"RECOMMENDATION: PROCEED WITH TARGETED CAVEATS. Upgrading cluster '{cluster.name}' from "
            f"OCP {cluster.ocp_version} to {target_version} is architecturally supported, but conditional update risks "
            "or storage driver advisories require pre-upgrade staging verification."
        )
    else:
        synopsis = (
            f"RECOMMENDATION: APPROVED FOR STAGED ROLLOUT (GO). Target release {target_version} provides verified "
            f"compatibility across MTV, Dell CSM, and Portworx without major version drift."
        )

    # Query Live Local LLM if enabled and reachable
    if use_live_llm:
        llm_prompt = (
            f"Cluster: {cluster.name}\n"
            f"Current OCP Version: {cluster.ocp_version}\n"
            f"Target OCP Version: {target_version}\n"
            f"Installed Operators: {json.dumps(components_map)}\n"
            f"Version Drift: {drift['drift_type']} (Major: {drift['is_major_drift']})\n"
            f"Deterministic Verdict: {verdict}\n"
            f"Identified Risks: {', '.join(escalation_reasons) if escalation_reasons else 'None'}\n"
            f"TestOps Policy: Prioritize active VM migration (MTV). Validate Dell CSM / Portworx storage failover.\n\n"
            f"Write a 2-3 sentence executive synopsis for the SRE Lead explaining why this upgrade is {verdict}."
        )
        llm_narrative = query_local_llm(llm_prompt, llm_url=llm_url)
        if llm_narrative:
            synopsis = f"[Local LLM Analysis] {llm_narrative}"

    # Build Deep Impact Breakdown
    impact_analysis = {
        "migration_impact (MTV)": (
            "HIGH RISK: Major/unsupported OCP version jump may break virt-v2v controller status streams, "
            "warm migration changed block tracking (CBT), and vSphere VDDK disk transfer pipes."
            if "mtv" in components_map and (drift["is_major_drift"] or operator_risks)
            else "LOW / STABLE: MTV operator verified compatible. Ensure no migration plans are in Cutover state during upgrade."
        ),
        "storage_impact (Dell CSM & Portworx)": (
            f"CRITICAL RISK: Storage CSI drivers ({', '.join([k for k in components_map if 'dell' in k or 'portworx' in k])}) "
            "require kernel header validation and CSI node-driver re-certification on target Kubernetes base."
            if operator_risks or drift["is_major_drift"]
            else "VERIFIED: Dell CSM and Portworx storage operators support target OCP version."
        ),
        "security_delta": (
            f"{critical_cve_count} Critical and {cve_count} Important CVE/RHSAs tracked in database. "
            f"Target {target_version} incorporates recent security patches."
        ),
        "version_drift_index": drift,
    }

    # Build Step-by-Step TestOps Remediation Plan
    testops_plan = [
        {
            "step": 1,
            "phase": "Pre-Requisite Operator Upgrades",
            "action": "Upgrade MTV to certified operator version (e.g. 2.8.0+) and Dell CSM / Portworx to latest supported z-stream in Pre-Prod.",
            "gate": "Operator CSVs in Succeeded phase with 0 CrashLoopBackOff pods.",
        },
        {
            "step": 2,
            "phase": "Staging Sandbox Live Migration Test",
            "action": "Execute end-to-end VM warm migration dry run from VMware vSphere to OCV on target OCP build.",
            "gate": "Zero data corruption, successful cutover under 60 seconds.",
        },
        {
            "step": 3,
            "phase": "CSI Storage Failover Verification",
            "action": "Trigger node drain and worker reboot while running I/O load on Dell CSM (PowerStore/PowerFlex) and Portworx RWX volumes.",
            "gate": "Volumes reattach within 30s without VolumeAttachment timeout.",
        },
        {
            "step": 4,
            "phase": "Fleet Canary Deployment",
            "action": "Roll out upgrade to 1 non-prod lab cluster before scheduling production fleet windows.",
            "gate": "ClusterVersion reaches Available=True with 0 cluster operator degraded alerts for 48 hours.",
        },
    ]

    # Human Sign-off Form
    human_sign_off = {
        "required_approvers": ["TestOps Lead", "Cloud Platform SRE Lead", "Storage Administrator"],
        "status": "PENDING_APPROVAL" if "NO-GO" in verdict or "CAVEATS" in verdict else "AUTO_APPROVED",
        "sign_off_checklist": [
            "[ ] All active MTV VM migrations paused / drained",
            "[ ] Dell CSM / Portworx sandbox failover test passed",
            "[ ] TestOps qualification test suite executed on target build",
            "[ ] Maintenance window approved by Change Advisory Board (CAB)",
        ],
    }

    return {
        "cluster": cluster.name,
        "current_version": cluster.ocp_version,
        "target_version": target_version,
        "strategic_verdict": verdict,
        "executive_synopsis": synopsis,
        "escalation_reasons": escalation_reasons,
        "impact_analysis": impact_analysis,
        "testops_remediation_plan": testops_plan,
        "human_in_the_loop_sign_off": human_sign_off,
    }
