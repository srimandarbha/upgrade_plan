"""Live cluster collector -> component_versions table (+ raw conditional-update
data available to the compatibility engine).

Reads two things directly off each cluster rather than re-deriving them:

1. The `ClusterVersion` object (config.openshift.io/v1, cluster-scoped,
   name "version"). Its `status.conditionalUpdates[].risks[]` is the CVO's own
   PromQL-evaluated answer to "does this known risk apply to *this* cluster" --
   there's no PromQL to reimplement here, just read the field.
2. Installed `ClusterServiceVersion` objects (operators.coreos.com/v1alpha1,
   namespaced), filtered to the components you care about, to get installed
   OCV / Dell CSM / Portworx versions.

Fetch and parse are kept separate on purpose: parse_clusterversion() and
parse_csvs() are pure functions you can unit-test against a saved fixture
without a live cluster (see tests/test_cluster_state.py).

Auth: this expects a kubeconfig with a context per cluster (set
clusters.kubeconfig_context in your inventory) or, if run from inside a hub
cluster with RHACM, you'd swap fetch_clusterversion/fetch_csvs for calls
against the ACM Search API instead -- the parse functions don't change.
"""
from __future__ import annotations

import argparse
import logging
import re

from kubernetes import client, config

from db.db import get_session
from db.models import ComponentVersion, Cluster

log = logging.getLogger(__name__)

CV_GROUP, CV_VERSION, CV_PLURAL = "config.openshift.io", "v1", "clusterversions"
CSV_GROUP, CSV_VERSION, CSV_PLURAL = "operators.coreos.com", "v1alpha1", "clusterserviceversions"

# component key -> regex matched against CSV metadata.name
COMPONENT_CSV_PATTERNS: dict[str, re.Pattern] = {
    "ocv": re.compile(r"^kubevirt-hyperconverged-operator\."),
    "dell-csm": re.compile(r"^dell-csm-operator\."),
    "portworx": re.compile(r"^portworx-(operator|certified)\."),
}


def load_api_clients(context: str | None = None, kubeconfig_path: str | None = None):
    config.load_kube_config(config_file=kubeconfig_path, context=context)
    return client.CustomObjectsApi()


def fetch_clusterversion(api: "client.CustomObjectsApi") -> dict:
    return api.get_cluster_custom_object(CV_GROUP, CV_VERSION, CV_PLURAL, "version")


def fetch_csvs(api: "client.CustomObjectsApi") -> list[dict]:
    result = api.list_cluster_custom_object(CSV_GROUP, CSV_VERSION, CSV_PLURAL)
    return result.get("items", [])


def parse_clusterversion(cv: dict) -> dict:
    status = cv.get("status", {})
    desired = status.get("desired", {})
    return {
        "version": desired.get("version"),
        "channel": cv.get("spec", {}).get("channel"),
        "available_updates": status.get("availableUpdates") or [],
        "conditional_updates": status.get("conditionalUpdates") or [],
    }


def parse_csvs(csvs: list[dict]) -> list[dict]:
    """Return one row per recognized component: {component, version, namespace, csv_name}."""
    rows = []
    for csv in csvs:
        name = csv.get("metadata", {}).get("name", "")
        namespace = csv.get("metadata", {}).get("namespace")
        phase = csv.get("status", {}).get("phase")
        if phase and phase != "Succeeded":
            continue  # skip installs that aren't actually healthy
        for component, pattern in COMPONENT_CSV_PATTERNS.items():
            if pattern.match(name):
                version = csv.get("spec", {}).get("version")
                if not version and ".v" in name:
                    version = name.split(".v", 1)[1]
                rows.append(
                    {
                        "component": component,
                        "version": version or "unknown",
                        "namespace": namespace,
                        "csv_name": name,
                    }
                )
    return rows


def upsert_component_versions(session, cluster_id: int, rows: list[dict]) -> int:
    for row in rows:
        existing = (
            session.query(ComponentVersion)
            .filter_by(cluster_id=cluster_id, component=row["component"])
            .one_or_none()
        )
        if existing:
            existing.version = row["version"]
            existing.namespace = row["namespace"]
            existing.csv_name = row["csv_name"]
        else:
            session.add(ComponentVersion(cluster_id=cluster_id, **row))
    # always keep the ocp entry current too
    return len(rows)


def collect_for_cluster(cluster_name: str, kubeconfig_path: str | None = None) -> int:
    with get_session() as db:
        cluster = db.query(Cluster).filter_by(name=cluster_name).one_or_none()
        if cluster is None:
            log.warning("Cluster %s not found in inventory; skipping", cluster_name)
            return 0
        try:
            api = load_api_clients(context=cluster.kubeconfig_context, kubeconfig_path=kubeconfig_path)
            cv = parse_clusterversion(fetch_clusterversion(api))
            csv_rows = parse_csvs(fetch_csvs(api))
        except Exception as exc:  # noqa: BLE001 - a single unreachable cluster shouldn't kill the run
            log.warning("Could not collect from %s: %s", cluster_name, exc)
            return 0

        if cv.get("version"):
            cluster.ocp_version = cv["version"]
            csv_rows.append(
                {"component": "ocp", "version": cv["version"], "namespace": None, "csv_name": None}
            )
        n = upsert_component_versions(db, cluster.id, csv_rows)
        # Conditional-update risk data is per-cluster and time-sensitive; hand it
        # straight to the compatibility engine rather than persisting it here --
        # see engine/compatibility.py (next milestone) for where this goes.
        log.info(
            "%s: %d component rows, %d conditional-update risks currently reported",
            cluster_name, n, len(cv.get("conditional_updates", [])),
        )
        return n


def collect(cluster_names: list[str] | None = None, kubeconfig_path: str | None = None) -> int:
    with get_session() as db:
        names = cluster_names or [c.name for c in db.query(Cluster).all()]
    total = 0
    for name in names:
        total += collect_for_cluster(name, kubeconfig_path=kubeconfig_path)
    return total


def main():
    logging.basicConfig(level=logging.INFO)
    ap = argparse.ArgumentParser(description="Collect live ClusterVersion + operator state per cluster")
    ap.add_argument("--cluster", action="append", help="repeatable; default: every cluster in inventory")
    ap.add_argument("--kubeconfig", help="path to a kubeconfig with a context per cluster")
    args = ap.parse_args()
    n = collect(cluster_names=args.cluster, kubeconfig_path=args.kubeconfig)
    log.info("Upserted %d component_versions rows total", n)


if __name__ == "__main__":
    main()
