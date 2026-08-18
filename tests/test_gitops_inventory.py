from pathlib import Path
import pytest

from collectors.gitops_inventory import (
    discover_clusters_and_operators,
    normalize_component_name,
    parse_subscription_manifest,
    upsert_gitops_fleet,
)
from db.models import Cluster, ComponentVersion


def test_normalize_component_name():
    assert normalize_component_name("kubevirt-hyperconverged-operator") == "ocv"
    assert normalize_component_name("dell-csm-operator") == "dell-csm"
    assert normalize_component_name("portworx-operator") == "portworx"
    assert normalize_component_name("mtv-operator") == "mtv"


def test_parse_subscription_manifest():
    doc = {
        "apiVersion": "operators.coreos.com/v1alpha1",
        "kind": "Subscription",
        "metadata": {
            "name": "kubevirt-hyperconverged",
            "namespace": "openshift-cnv",
        },
        "spec": {
            "channel": "stable-4.22",
            "installPlanApproval": "Automatic",
            "name": "kubevirt-hyperconverged",
            "source": "redhat-operators",
            "startingCSV": "kubevirt-hyperconverged.v4.22.0",
        },
    }
    sub = parse_subscription_manifest(doc)
    assert sub is not None
    assert sub["component"] == "ocv"
    assert sub["version"] == "4.22.0"
    assert sub["channel"] == "stable-4.22"
    assert sub["namespace"] == "openshift-cnv"


def test_discover_and_upsert_gitops_fleet(tmp_path, db_session):
    # Setup mock redhat-cop repository layout
    repo_root = tmp_path / "gitops-repo"
    
    # 1. Components operator definition
    comp_dir = repo_root / "components" / "operators" / "dell-csm"
    comp_dir.mkdir(parents=True)
    (comp_dir / "subscription.yaml").write_text(
        """apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: dell-csm-operator
  namespace: dell-csm
spec:
  channel: stable
  name: dell-csm-operator
  startingCSV: dell-csm-operator.v1.13.0
""",
        encoding="utf-8",
    )

    # 2. Cluster overlays for 2 clusters
    for name in ("east-prod-01", "west-prod-02"):
        cluster_dir = repo_root / "clusters" / name
        cluster_dir.mkdir(parents=True)
        (cluster_dir / "ocv-subscription.yaml").write_text(
            f"""apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: kubevirt-hyperconverged
  namespace: openshift-cnv
spec:
  channel: stable-4.22
  name: kubevirt-hyperconverged
  startingCSV: kubevirt-hyperconverged.v4.22.0
""",
            encoding="utf-8",
        )
        (cluster_dir / "cluster-curator.yaml").write_text(
            f"""apiVersion: cluster.open-cluster-management.io/v1beta1
kind: ClusterCurator
metadata:
  name: {name}
spec:
  upgrade:
    desiredUpdate: "4.22.2"
""",
            encoding="utf-8",
        )

    fleet = discover_clusters_and_operators(repo_root)
    assert len(fleet) == 2
    assert "east-prod-01" in fleet
    assert "west-prod-02" in fleet
    assert fleet["east-prod-01"]["ocp_version"] == "4.22.2"
    assert "ocv" in fleet["east-prod-01"]["operators"]
    assert "dell-csm" in fleet["east-prod-01"]["operators"]

    n_c, n_ops = upsert_gitops_fleet(db_session, fleet)
    db_session.commit()

    assert n_c == 2
    assert n_ops >= 4
    assert db_session.query(Cluster).filter_by(name="east-prod-01").count() == 1
    c = db_session.query(Cluster).filter_by(name="east-prod-01").one()
    assert db_session.query(ComponentVersion).filter_by(cluster_id=c.id, component="ocv").count() == 1
