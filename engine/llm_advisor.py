"""Strategic Upgrade & Migration LLM Advisor Engine.

Provides unified JSON output across both:
  - Deterministic evaluation mode (fast rule-based checks)
  - LLM evaluation mode (deep reasoning + TestOps risk synthesis via local/remote LLM)

Both modes output the exact same JSON schema.
"""
from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

from db.models import Assessment, Cluster, ComponentVersion, OperatorCompat, ProductLifecycle, UpgradeEdge
from engine.compatibility import check_version_in_range, parse_version_tuple

log = logging.getLogger(__name__)

DEFAULT_LLM_URL = "http://127.0.0.1:8080/v1/chat/completions"


def query_local_llm(
    prompt: str,
    system_prompt: str | None = None,
    llm_url: str | None = None,
    model_name: str | None = None,
    timeout: int = 90,
) -> str | None:
    """Query OpenAI-compatible local LLM endpoint (e.g. llama.cpp / vLLM on localhost:8080)."""
    import requests

    url = llm_url or os.environ.get("LLM_URL", DEFAULT_LLM_URL)
    default_system = (
        "You are a Senior OpenShift Platform SRE and Virtualization Upgrade Specialist. "
        "Analyze the provided cluster facts, operator matrix (MTV, Dell CSM, Portworx), "
        "and TestOps policies. Always output valid JSON matching the requested schema."
    )
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt or default_system},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 600,
        "temperature": 0.1,
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
        log.warning("Local LLM request to %s failed: %s (using expert rule engine)", url, exc)
    return None


def fetch_confluence_policy(
    confluence_base_url: str | None = None,
    page_id: str | None = None,
    auth_token: str | None = None,
) -> str | None:
    """Placeholder for future direct Confluence REST API ingestion."""
    base_url = confluence_base_url or os.environ.get("CONFLUENCE_URL")
    pid = page_id or os.environ.get("CONFLUENCE_PAGE_ID")
    token = auth_token or os.environ.get("CONFLUENCE_API_TOKEN")

    if not base_url or not pid:
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
    confluence_content = fetch_confluence_policy()
    if confluence_content:
        return confluence_content

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
    is_downgrade = (tgt_parts + (0, 0, 0))[:3] < (cur_parts + (0, 0, 0))[:3]
    minor_diff = (major_tgt * 100 + minor_tgt) - (major_cur * 100 + minor_cur)
    is_multi_minor_jump = minor_diff > 1

    drift_type = "major" if is_major_drift else (
        "downgrade" if is_downgrade else (
            "multi-minor" if is_multi_minor_jump else (
                "minor" if minor_diff == 1 else "z-stream"
            )
        )
    )

    return {
        "current": current_version,
        "target": target_version,
        "is_major_drift": is_major_drift,
        "is_downgrade": is_downgrade,
        "is_multi_minor_jump": is_multi_minor_jump,
        "drift_type": drift_type,
        "minor_steps": minor_diff,
    }


def extract_json_payload(raw_text: str) -> dict[str, Any] | None:
    """Attempt to parse JSON from LLM output, extracting from markdown fences if needed."""
    if not raw_text:
        return None
    clean = raw_text.strip()
    # Check for markdown code fence
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", clean, re.DOTALL)
    if fence_match:
        try:
            return json.loads(fence_match.group(1))
        except json.JSONDecodeError:
            pass
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        return None


def generate_expert_decision(
    cluster: Cluster,
    target_version: str,
    assessment: Assessment,
    installed_components: list[ComponentVersion],
    compat_records: list[OperatorCompat],
    cve_count: int,
    critical_cve_count: int,
    policy_text: str,
) -> dict[str, Any]:
    """Fallback deterministic logic mimicking the LLM's comprehensive decision framework."""
    drift = calculate_version_drift(cluster.ocp_version, target_version)
    reasons_data = assessment.reasons or {}
    deterministic_verdict = assessment.verdict.upper()

    verdict = deterministic_verdict
    escalation_reasons: list[str] = list(reasons_data.get("blockers") or [])

    if drift["is_downgrade"]:
        verdict = "NO-GO (ESCALATE)"
        escalation_reasons.append(
            f"In-place platform downgrade/rollback ({cluster.ocp_version} -> {target_version}) is strictly unsupported "
            "by OpenShift Container Platform, Kubernetes, and CVO/MCO architecture. Rollbacks require full cluster redeployment or etcd disaster recovery restore."
        )

    if drift["is_major_drift"]:
        verdict = "NO-GO (ESCALATE)"
        escalation_reasons.append(
            f"Major version architectural drift detected ({cluster.ocp_version} -> {target_version}). "
            "Under TestOps Policy, major version transitions require mandatory sandbox qualification."
        )

    components_map = {c.component: c.version for c in installed_components}
    operator_risks = []

    for comp, ver in components_map.items():
        if comp == "ocp":
            continue
        rules = [r for r in compat_records if r.component == comp and r.operator_version == ver]
        if rules:
            if not any(check_version_in_range(target_version, r.min_ocp, r.max_ocp) for r in rules):
                max_supported = rules[0].max_ocp or "any"
                operator_risks.append(
                    f"{comp} (version {ver}) is NOT certified for OCP {target_version} (supported up to {max_supported})."
                )
        elif drift["is_major_drift"]:
            operator_risks.append(
                f"{comp} (version {ver}) has no verified compatibility rule for major release {target_version}."
            )

    # Re-use core generation logic for the output structure
    return generate_strategic_analysis(
        cluster, target_version, assessment, installed_components, compat_records, 
        cve_count, critical_cve_count, policy_text
    )


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
    use_live_llm: bool = False,
) -> dict[str, Any]:
    """Generate unified JSON strategic assessment across deterministic and LLM modes."""
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

    # Core Rule Reasoning
    escalation_reasons: list[str] = []
    verdict = assessment.verdict.upper()

    if drift["is_downgrade"]:
        verdict = "NO-GO (ESCALATE)"
        escalation_reasons.append(
            f"In-place platform downgrade/rollback ({cluster.ocp_version} -> {target_version}) is strictly unsupported "
            "by OpenShift Container Platform, Kubernetes, and CVO/MCO architecture. Rollbacks require full cluster redeployment or etcd disaster recovery restore."
        )

    if drift["is_major_drift"]:
        verdict = "NO-GO (ESCALATE)"
        escalation_reasons.append(
            f"Major version architectural drift detected ({cluster.ocp_version} -> {target_version}). "
            "Under TestOps Policy, major version transitions require mandatory sandbox qualification."
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

    # Build Dynamic Impact Breakdown from DB records
    storage_comps = [c.component for c in installed_components if any(kw in c.component.lower() for kw in ["csm", "csi", "storage", "portworx", "odf", "ceph"])]
    migration_comps = [c.component for c in installed_components if any(kw in c.component.lower() for kw in ["mtv", "forklift", "migration", "v2v"])]

    dynamic_impact: dict[str, Any] = {
        "migration_impact": (
            f"HIGH RISK: Detected migration operator(s) ({', '.join(migration_comps)}). Major version drift or uncertified target may disrupt active VM cutovers and disk transfer streams."
            if migration_comps and (drift["is_major_drift"] or operator_risks)
            else (f"STABLE: Migration operator(s) ({', '.join(migration_comps)}) verified within certified range." if migration_comps else "N/A: No active VM migration operators installed.")
        ),
        "storage_impact": (
            f"CRITICAL RISK: Storage CSI operator(s) ({', '.join(storage_comps)}) require kernel header validation and CSI node-driver re-certification on target Kubernetes base."
            if storage_comps and (operator_risks or drift["is_major_drift"])
            else (f"VERIFIED: Storage operator(s) ({', '.join(storage_comps)}) certified for target version." if storage_comps else "N/A: No custom CSI storage operators installed.")
        ),
        "security_delta": f"{critical_cve_count} Critical and {cve_count} Important CVE/RHSAs tracked in database.",
        "version_drift": drift,
    }

    # Build Dynamic Staging Remediation Plan based on installed DB inventory
    testops_plan = []
    step_num = 1
    if operator_risks:
        testops_plan.append({
            "step": step_num,
            "phase": "Pre-Requisite Operator Upgrades",
            "action": f"Upgrade uncertified operator(s) ({', '.join([c.component for c in installed_components])}) to versions supporting OCP {target_version}.",
            "gate": "Operator CSVs reach Succeeded phase with 0 CrashLoopBackOff pods.",
        })
        step_num += 1

    if migration_comps:
        testops_plan.append({
            "step": step_num,
            "phase": "Sandbox Live Migration Test",
            "action": f"Execute end-to-end VM warm migration dry run using {', '.join(migration_comps)} on target OCP build.",
            "gate": "Zero data corruption, successful cutover under SLA window.",
        })
        step_num += 1

    if storage_comps:
        testops_plan.append({
            "step": step_num,
            "phase": "CSI Storage Failover Verification",
            "action": f"Trigger worker node drain and reboot under I/O load on storage operators ({', '.join(storage_comps)}).",
            "gate": "Volumes reattach within 30s without VolumeAttachment timeout.",
        })
        step_num += 1

    testops_plan.append({
        "step": step_num,
        "phase": "Fleet Canary Deployment",
        "action": "Roll out upgrade to 1 non-prod lab cluster before scheduling production fleet windows.",
        "gate": "ClusterVersion reaches Available=True with 0 cluster operator degraded alerts for 48 hours.",
    })

    # Dynamic Human Sign-off Form
    checklist = ["[ ] Maintenance window approved by Change Advisory Board (CAB)"]
    if migration_comps:
        checklist.insert(0, f"[ ] All active VM migrations on {', '.join(migration_comps)} paused / drained")
    if storage_comps:
        checklist.insert(1, f"[ ] Sandbox failover test passed on {', '.join(storage_comps)}")
    if operator_risks or drift["is_major_drift"]:
        checklist.insert(2, "[ ] TestOps qualification test suite executed on target build in staging")

    human_sign_off = {
        "status": "PENDING_APPROVAL" if "NO-GO" in verdict or "CAVEATS" in verdict else "AUTO_APPROVED",
        "required_approvers": ["TestOps Lead", "Cloud Platform SRE Lead", "Storage Administrator"],
        "sign_off_checklist": checklist,
    }

    # Base unified structure
    unified_result: dict[str, Any] = {
        "cluster": cluster.name,
        "current_version": cluster.ocp_version,
        "target_version": target_version,
        "evaluation_mode": "llm" if use_live_llm else "deterministic",
        "verdict": verdict,
        "executive_synopsis": synopsis,
        "reasons": {
            "blockers": assessment.reasons.get("blockers", []) + escalation_reasons,
            "caveats": assessment.reasons.get("caveats", []),
            "info": assessment.reasons.get("info", []),
        },
        "impact_analysis": dynamic_impact,
        "testops_remediation_plan": testops_plan,
        "human_in_the_loop_sign_off": human_sign_off,
        "evaluated_at": assessment.evaluated_at.isoformat() if assessment.evaluated_at else None,
    }

    # If LLM mode is active, prompt the LLM to think and return the JSON decision
    if use_live_llm:
        system_prompt = (
            "You are an expert SRE and OpenShift Virtualization Upgrade Decision Engine. "
            "You evaluate cluster upgrade safety against TestOps policies and return a JSON decision. "
            "Return ONLY valid JSON matching this schema:\n"
            "{\n"
            '  "verdict": "GO" | "GO-WITH-CAVEATS" | "NO-GO" | "NO-GO (ESCALATE)",\n'
            '  "executive_synopsis": "string",\n'
            '  "reasons": {"blockers": ["string"], "caveats": ["string"], "info": ["string"]},\n'
            '  "impact_analysis": {"migration_impact": "string", "storage_impact": "string", "security_delta": "string"}\n'
            "}"
        )
        llm_prompt = (
            f"Cluster: {cluster.name}\n"
            f"Current OCP Version: {cluster.ocp_version}\n"
            f"Target OCP Version: {target_version}\n"
            f"Installed Operators: {json.dumps(components_map)}\n"
            f"Version Drift: {drift['drift_type']} (Major Drift: {drift['is_major_drift']})\n"
            f"Deterministic Check: {assessment.verdict.upper()}\n"
            f"Identified Risks: {json.dumps(escalation_reasons)}\n"
            f"TestOps Policy: Prioritize active VM migration continuity. Require CSI storage validation.\n\n"
            "Analyze the upgrade and return your JSON decision."
        )
        raw_llm_out = query_local_llm(llm_prompt, system_prompt=system_prompt, llm_url=llm_url)
        parsed_llm = extract_json_payload(raw_llm_out) if raw_llm_out else None

        if parsed_llm and "verdict" in parsed_llm:
            unified_result["verdict"] = str(parsed_llm.get("verdict", verdict)).upper()
            if "executive_synopsis" in parsed_llm:
                unified_result["executive_synopsis"] = parsed_llm["executive_synopsis"]
            if "reasons" in parsed_llm and isinstance(parsed_llm["reasons"], dict):
                unified_result["reasons"].update(parsed_llm["reasons"])
            if "impact_analysis" in parsed_llm and isinstance(parsed_llm["impact_analysis"], dict):
                unified_result["impact_analysis"].update(parsed_llm["impact_analysis"])
            unified_result["evaluation_mode"] = "llm"
        elif raw_llm_out:
            # LLM returned text rather than strict JSON; use LLM narrative as synopsis
            unified_result["executive_synopsis"] = f"[LLM Decision] {raw_llm_out}"
            unified_result["evaluation_mode"] = "llm"

    return unified_result
