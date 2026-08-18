"""GitOps Standards Inventory Collector (`redhat-cop` template standard).

Discovers and maps cluster-wise operator subscriptions and target OCP versions
directly from an internal GitOps repository structured according to:
https://github.com/redhat-cop/gitops-standards-repo-template

Parses:
- `clusters/<cluster-name>/`: cluster declarations and overlays
- `components/operators/`: Subscription CRDs (channel, startingCSV, package)
- `kustomization.yaml`: overlay references

Populates:
- `clusters` table (50+ clusters)
- `component_versions` table (operator versions per cluster)
"""
from __future__ import annotations

import argparse
import logging
import os
import re
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from db.db import get_session
from db.models import Cluster, ComponentVersion

log = logging.getLogger(__name__)

# Operator name mapping: GitOps Subscription spec.name/metadata.name -> standard component key
OPERATOR_NAME_MAP = {
    "kubevirt-hyperconverged": "ocv",
    "kubevirt-hyperconverged-operator": "ocv",
    "hco-operator": "ocv",
    "dell-csm-operator": "dell-csm",
    "dell-csm": "dell-csm",
    "portworx-operator": "portworx",
    "portworx-certified": "portworx",
    "portworx": "portworx",
    "mtv-operator": "mtv",
    "forklift-operator": "mtv",
    "openshift-gitops-operator": "gitops",
    "openshift-pipelines-operator-rh": "pipelines",
    "odf-operator": "odf",
    "ocs-operator": "ocs",
}


def normalize_component_name(raw_name: str) -> str:
    """Map raw subscription or package name to canonical component name."""
    clean = raw_name.lower().strip()
    for pattern, canonical in OPERATOR_NAME_MAP.items():
        if pattern in clean:
            return canonical
    return clean


def extract_version_from_csv(starting_csv: str | None, channel: str | None) -> str:
    """Extract semantic version from startingCSV (e.g. 'dell-csm-operator.v1.13.0' -> '1.13.0') or channel."""
    if starting_csv:
        match = re.search(r"[vV]?(\d+\.\d+(\.\d+)?)", starting_csv)
        if match:
            return match.group(1)
    if channel:
        match = re.search(r"(\d+\.\d+(\.\d+)?)", channel)
        if match:
            return match.group(1)
    return "latest"


def parse_subscription_manifest(doc: dict[str, Any]) -> dict[str, Any] | None:
    """Parse a single Kubernetes Subscription YAML document."""
    if not isinstance(doc, dict):
        return None
    if doc.get("kind") != "Subscription":
        return None

    spec = doc.get("spec", {})
    metadata = doc.get("metadata", {})
    raw_name = spec.get("name") or metadata.get("name") or "unknown"
    component = normalize_component_name(raw_name)
    channel = spec.get("channel")
    starting_csv = spec.get("startingCSV")
    namespace = metadata.get("namespace") or spec.get("installPlanApproval")
    version = extract_version_from_csv(starting_csv, channel)

    return {
        "component": component,
        "version": version,
        "channel": channel,
        "namespace": namespace,
        "csv_name": starting_csv or f"{raw_name}.{version}",
    }


def parse_yaml_file(file_path: Path) -> list[dict[str, Any]]:
    """Parse all documents in a YAML file safely."""
    results = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            docs = yaml.safe_load_all(f)
            for d in docs:
                if isinstance(d, dict):
                    results.append(d)
    except Exception as exc:
        log.debug("Skipping unparseable YAML file %s: %s", file_path, exc)
    return results


def discover_clusters_and_operators(repo_root: Path | str) -> dict[str, dict[str, Any]]:
    """Scan redhat-cop GitOps template directory and extract cluster operator inventory.

    Returns dict mapping:
        cluster_name -> {
            "ocp_version": str,
            "region": str,
            "env": str,
            "operators": {component: {version, channel, namespace, csv_name}}
        }
    """
    root = Path(repo_root)
    clusters_dir = root / "clusters"
    if not clusters_dir.exists():
        clusters_dir = root

    fleet: dict[str, dict[str, Any]] = {}

    # 1. First, parse all shared component operator definitions
    shared_operators: dict[str, dict[str, Any]] = {}
    components_dir = root / "components"
    if components_dir.exists():
        for yfile in components_dir.rglob("*.yaml"):
            for doc in parse_yaml_file(yfile):
                sub = parse_subscription_manifest(doc)
                if sub:
                    shared_operators[sub["component"]] = sub

    # 2. Discover and parse each cluster under clusters/<cluster_name>/
    for cluster_path in clusters_dir.iterdir():
        if not cluster_path.is_dir() or cluster_path.name.startswith("."):
            continue

        cluster_name = cluster_path.name
        cluster_data: dict[str, Any] = {
            "ocp_version": "4.20.0",
            "region": "us-east-1",
            "env": "prod" if "prod" in cluster_name else "non-prod",
            "operators": dict(shared_operators),  # baseline with shared components
        }

        # Scan all YAML manifests within this cluster overlay
        for yfile in cluster_path.rglob("*.yaml"):
            for doc in parse_yaml_file(yfile):
                # Check for Subscription manifests
                sub = parse_subscription_manifest(doc)
                if sub:
                    cluster_data["operators"][sub["component"]] = sub

                # Check for ClusterCurator / ClusterDeployment for OCP target version
                if doc.get("kind") in ("ClusterCurator", "ClusterDeployment"):
                    desired = doc.get("spec", {}).get("upgrade", {}).get("desiredUpdate")
                    if desired:
                        cluster_data["ocp_version"] = str(desired)

                # Check metadata labels
                labels = doc.get("metadata", {}).get("labels", {})
                if "environment" in labels:
                    cluster_data["env"] = labels["environment"]
                if "region" in labels:
                    cluster_data["region"] = labels["region"]

        fleet[cluster_name] = cluster_data

    return fleet


def upsert_gitops_fleet(session: Session, fleet: dict[str, dict[str, Any]]) -> tuple[int, int]:
    """Persist discovered clusters and their component versions into PostgreSQL."""
    n_clusters = 0
    n_components = 0

    for cluster_name, data in fleet.items():
        # Upsert Cluster
        cluster_stmt = (
            pg_insert(Cluster)
            .values(
                name=cluster_name,
                region=data.get("region", "us-east-1"),
                env=data.get("env", "prod"),
                ocp_version=data.get("ocp_version", "4.20.0"),
                connected=False,
            )
            .on_conflict_do_update(
                index_elements=["name"],
                set_={"ocp_version": data.get("ocp_version", "4.20.0")},
            )
            .returning(Cluster.id)
        )
        res = session.execute(cluster_stmt)
        cluster_id = res.scalar_one()
        n_clusters += 1

        # Upsert Component Versions
        comp_rows = []
        for comp_name, op in data.get("operators", {}).items():
            comp_rows.append({
                "cluster_id": cluster_id,
                "component": op["component"],
                "version": op["version"],
                "channel": op.get("channel"),
                "namespace": op.get("namespace"),
                "csv_name": op.get("csv_name"),
            })

        if comp_rows:
            comp_stmt = pg_insert(ComponentVersion).values(comp_rows)
            comp_stmt = comp_stmt.on_conflict_do_update(
                index_elements=["cluster_id", "component"],
                set_={
                    "version": comp_stmt.excluded.version,
                    "channel": comp_stmt.excluded.channel,
                    "namespace": comp_stmt.excluded.namespace,
                    "csv_name": comp_stmt.excluded.csv_name,
                },
            )
            session.execute(comp_stmt)
            n_components += len(comp_rows)

    return n_clusters, n_components


def collect(gitops_dir: Path | str | None = None, git_repo_url: str | None = None) -> tuple[int, int]:
    """Collect cluster-wise operator mappings from redhat-cop GitOps template directory."""
    target_path = gitops_dir
    if not target_path and not git_repo_url:
        # Default to local data directory if available
        default_dir = Path(__file__).resolve().parents[1] / "data" / "gitops_sample_repo"
        if default_dir.exists():
            target_path = default_dir
        else:
            log.info("No --gitops-dir or --gitops-repo supplied for gitops-inventory collector.")
            return 0, 0

    if git_repo_url and not target_path:
        import tempfile
        import git
        tmp_dir = tempfile.mkdtemp(prefix="gitops-standards-")
        log.info("Cloning GitOps standards repository from %s into %s", git_repo_url, tmp_dir)
        git.Repo.clone_from(git_repo_url, tmp_dir, depth=1)
        target_path = Path(tmp_dir)

    fleet = discover_clusters_and_operators(target_path)
    log.info("Discovered %d clusters from GitOps standards repository at %s", len(fleet), target_path)

    with get_session() as db:
        n_clusters, n_components = upsert_gitops_fleet(db, fleet)

    return n_clusters, n_components


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description="Ingest cluster operator mappings from redhat-cop GitOps repository")
    ap.add_argument("--gitops-dir", type=Path, help="path to local clone of gitops-standards repository")
    ap.add_argument("--gitops-repo", help="remote Git URL of gitops-standards repository to clone")
    args = ap.parse_args()

    n_c, n_ops = collect(gitops_dir=args.gitops_dir, git_repo_url=args.gitops_repo)
    log.info("Successfully synced %d clusters and %d component versions to PostgreSQL", n_c, n_ops)


if __name__ == "__main__":
    main()
