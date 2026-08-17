from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from ruamel.yaml import YAML

from gitops.bot import (
    RepoTarget,
    create_yaml_parser,
    open_or_update_pr,
    render_pr_body,
    update_cluster_manifests,
)
from run_gitops_pr import load_target

TARGETS_FILE = Path(__file__).resolve().parents[1] / "data" / "gitops_targets.yaml"


def test_load_target_success():
    target = load_target("east-prod-01", TARGETS_FILE)
    assert isinstance(target, RepoTarget)
    assert target.owner == "example-org"
    assert target.repo_name == "ocp-gitops-fleet"
    assert target.cluster_path == "clusters/east-prod-01"
    assert target.curator_namespace == "east-prod-01"
    assert target.upstream_graph_url == "http://cincinnati.internal.net/api/upgrades_info/v1/graph"


def test_load_target_missing():
    with pytest.raises(SystemExit) as exc:
        load_target("nonexistent-cluster", TARGETS_FILE)
    assert "No GitOps repo config" in str(exc.value)


def test_update_cluster_manifests_preserves_comments(tmp_path):
    repo_root = tmp_path / "repo"
    cluster_dir = repo_root / "clusters" / "east-prod-01"
    cluster_dir.mkdir(parents=True)

    curator_file = cluster_dir / "cluster-curator.yaml"
    curator_content = """# ClusterCurator configuration for ACM fleet upgrades
apiVersion: cluster.open-cluster-management.io/v1beta1
kind: ClusterCurator
metadata:
  name: east-prod-01
  namespace: east-prod-01 # ACM cluster namespace
spec:
  desiredCuration: none
  upgrade:
    channel: stable-4.21 # Track stable channel
    desiredUpdate: "4.21.5"
"""
    curator_file.write_text(curator_content, encoding="utf-8")

    target = RepoTarget(
        repo_url="https://github.com/example-org/ocp-gitops-fleet.git",
        owner="example-org",
        repo_name="ocp-gitops-fleet",
        cluster_path="clusters/east-prod-01",
        curator_namespace="east-prod-01",
    )

    modified = update_cluster_manifests(repo_root, target, "east-prod-01", "4.22.8")
    assert len(modified) == 1
    assert "cluster-curator.yaml" in modified[0]

    updated_text = curator_file.read_text(encoding="utf-8")
    assert "ClusterCurator configuration for ACM fleet upgrades" in updated_text
    assert "# ACM cluster namespace" in updated_text
    assert 'desiredUpdate: "4.22.8"' in updated_text or "desiredUpdate: 4.22.8" in updated_text
    assert "desiredCuration: upgrade" in updated_text


def test_update_cluster_manifests_creates_new(tmp_path):
    repo_root = tmp_path / "repo"
    target = RepoTarget(
        repo_url="https://github.com/example-org/ocp-gitops-fleet.git",
        owner="example-org",
        repo_name="ocp-gitops-fleet",
        cluster_path="clusters/west-prod-01",
        curator_namespace="west-prod-01",
    )

    modified = update_cluster_manifests(repo_root, target, "west-prod-01", "4.22.8")
    assert len(modified) == 1
    created_file = repo_root / modified[0]
    assert created_file.exists()

    y = YAML()
    doc = y.load(created_file.read_text(encoding="utf-8"))
    assert doc["kind"] == "ClusterCurator"
    assert doc["spec"]["desiredCuration"] == "upgrade"
    assert doc["spec"]["upgrade"]["desiredUpdate"] == "4.22.8"


def test_render_pr_body():
    body = render_pr_body(
        cluster_name="east-prod-01",
        current_version="4.21.5",
        target_version="4.22.8",
        verdict="go-with-caveats",
        reasons={
            "caveats": ["Multus CNI conditional update notice"],
            "info": ["Upgrade path verified in Cincinnati graph"],
        },
        assessment_id=42,
        evaluated_at="2026-08-17T07:00:00Z",
    )
    assert "Automated Pre-Upgrade Assessment — east-prod-01" in body
    assert "4.21.5" in body
    assert "4.22.8" in body
    assert "GO WITH CAVEATS" in body
    assert "Multus CNI conditional update notice" in body
    assert "Pre-Merge Checklist" in body


def test_open_or_update_pr_dry_run():
    target = RepoTarget(
        repo_url="https://github.com/example-org/ocp-gitops-fleet.git",
        owner="example-org",
        repo_name="ocp-gitops-fleet",
        cluster_path="clusters/east-prod-01",
        curator_namespace="east-prod-01",
    )

    res = open_or_update_pr(
        cluster_name="east-prod-01",
        current_version="4.21.5",
        target_version="4.22.8",
        verdict="go",
        reasons={"info": ["Path verified"]},
        target=target,
        token="test-token",
        assessment_id=1,
        evaluated_at="2026-08-17T07:00:00Z",
        dry_run=True,
    )

    assert res["action"] == "dry-run-preview"
    assert res["cluster"] == "east-prod-01"
    assert res["target_version"] == "4.22.8"
    assert res["branch"] == "upgrade/east-prod-01-to-4.22.8"
    assert res["draft"] is False
    assert len(res["modified_files"]) > 0
    assert "diff" in res
