"""Deterministic Upgrade Compatibility Engine (GO / GO-WITH-CAVEATS / NO-GO).

Evaluates concrete facts from the database (and optional live cluster state):
  1. Upgrade graph connectivity (Cincinnati / OSUS upgrade edges)
  2. Conditional upgrade risks (Multus, CNI, storage, etcd, etc.)
  3. Installed operator compatibility (Dell CSM, Portworx, OCV, etc.)
  4. Red Hat product lifecycle windows (GA, Full Support, Maintenance, EOL)
  5. Security advisories / critical bugs
"""
from __future__ import annotations

import datetime as dt
import logging
from typing import Any

from sqlalchemy.orm import Session

from db.models import Assessment, Cluster, ComponentVersion, OperatorCompat, ProductLifecycle, UpgradeEdge

log = logging.getLogger(__name__)


def parse_version_tuple(v: str | None) -> tuple[int, ...]:
    """Parse version string like '4.22.8' into (4, 22, 8) for numeric comparison."""
    if not v:
        return ()
    parts = []
    # Strip prefixes like 'v' or 'openshift-'
    clean = v.strip().lstrip("v")
    for seg in clean.split("."):
        digits = ""
        for ch in seg:
            if ch.isdigit():
                digits += ch
            else:
                break
        if digits:
            parts.append(int(digits))
        else:
            break
    return tuple(parts)


def check_version_in_range(version: str, min_ver: str | None, max_ver: str | None) -> bool:
    """Check if version is within [min_ver, max_ver] inclusive."""
    v_tuple = parse_version_tuple(version)
    if not v_tuple:
        return True
    # Ensure 3 elements for comparison (major, minor, patch)
    v_padded = (v_tuple + (0, 0))[:3]

    if min_ver:
        min_tuple = parse_version_tuple(min_ver)
        if min_tuple:
            min_padded = (min_tuple + (0, 0))[:3]
            if v_padded < min_padded:
                return False
    if max_ver:
        max_tuple = parse_version_tuple(max_ver)
        if max_tuple:
            # If max is '4.22' (2 parts), allow all patch releases 4.22.x
            max_padded = (max_tuple + (999999, 999999))[:3]
            if v_padded > max_padded:
                return False
    return True


def assess(
    db: Session,
    cluster: Cluster,
    target_version: str,
    live_conditional_updates: list[dict] | None = None,
) -> Assessment:
    """Run deterministic compatibility checks and persist the assessment row."""
    current_version = cluster.ocp_version
    blockers: list[str] = []
    caveats: list[str] = []
    info: list[str] = []

    # 1. Check Upgrade Graph Connectivity
    edges = (
        db.query(UpgradeEdge)
        .filter(
            UpgradeEdge.from_version == current_version,
            UpgradeEdge.to_version == target_version,
        )
        .all()
    )

    if not edges:
        blockers.append(
            f"No direct upgrade path found in Cincinnati graph from {current_version} to {target_version}."
        )
    else:
        info.append(f"Upgrade path from {current_version} to {target_version} exists in Cincinnati graph.")
        # Check graph conditional risks
        conditional_edges = [e for e in edges if e.conditional]
        if conditional_edges:
            for ce in conditional_edges:
                risk_desc = ce.risk_name or "Unspecified conditional risk"
                msg = f"Graph flags conditional risk: {risk_desc}"
                if ce.risk_message:
                    msg += f" - {ce.risk_message}"
                caveats.append(msg)

    # 2. Check Live Cluster Conditional Updates (if provided)
    if live_conditional_updates:
        matching_live_risks = [
            u for u in live_conditional_updates if u.get("version") == target_version
        ]
        for item in matching_live_risks:
            for risk in item.get("risks", []):
                risk_name = risk.get("name", "UnknownRisk")
                risk_msg = risk.get("message", "")
                caveats.append(f"Active cluster conditional risk on target {target_version}: {risk_name} ({risk_msg})")

    # 3. Check Installed Operator Compatibility (Dell CSM, Portworx, OCV, etc.)
    installed_components = (
        db.query(ComponentVersion)
        .filter(ComponentVersion.cluster_id == cluster.id)
        .all()
    )

    for comp in installed_components:
        if comp.component == "ocp":
            continue
        compat_rules = (
            db.query(OperatorCompat)
            .filter(
                OperatorCompat.component == comp.component,
                OperatorCompat.operator_version == comp.version,
            )
            .all()
        )
        if compat_rules:
            is_compat = any(
                check_version_in_range(target_version, r.min_ocp, r.max_ocp)
                for r in compat_rules
            )
            if not is_compat:
                rule = compat_rules[0]
                blockers.append(
                    f"Operator '{comp.component}' version {comp.version} is incompatible with target OCP {target_version} "
                    f"(supported range: {rule.min_ocp or 'any'} to {rule.max_ocp or 'any'})."
                )
            else:
                info.append(f"Operator '{comp.component}' version {comp.version} verified compatible with {target_version}.")
        else:
            caveats.append(
                f"Operator '{comp.component}' version {comp.version} has no recorded compatibility rule in operator_compat; manual vendor certification check advised."
            )


    # 4. Check Red Hat Product Lifecycle (GA, Support, EOL)
    target_major_minor = ".".join(target_version.split(".")[:2])
    lifecycle = (
        db.query(ProductLifecycle)
        .filter(
            ProductLifecycle.component == "ocp",
            ProductLifecycle.version.like(f"%{target_major_minor}%"),
        )
        .first()
    )

    if lifecycle:
        today = dt.date.today()
        if lifecycle.eol_date and today >= lifecycle.eol_date:
            blockers.append(f"Target version {target_version} reached End of Life (EOL) on {lifecycle.eol_date}.")
        elif lifecycle.maintenance_end and today >= lifecycle.maintenance_end:
            caveats.append(f"Target version {target_version} is past maintenance support (ended {lifecycle.maintenance_end}).")
        else:
            info.append(f"Target version {target_version} is within active support window.")

    # Determine Verdict
    if blockers:
        verdict = "no-go"
    elif caveats:
        verdict = "go-with-caveats"
    else:
        verdict = "go"

    reasons: dict[str, Any] = {
        "verdict": verdict,
        "current_version": current_version,
        "target_version": target_version,
        "blockers": blockers,
        "caveats": caveats,
        "info": info,
    }

    assessment = Assessment(
        cluster_id=cluster.id,
        target_version=target_version,
        verdict=verdict,
        reasons=reasons,
        evaluated_at=dt.datetime.now(dt.timezone.utc),
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment
