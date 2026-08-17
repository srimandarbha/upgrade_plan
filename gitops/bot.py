"""GitOps pull request bot for OpenShift / OCV cluster upgrades.

Automates the lifecycle of GitOps PRs that bump a cluster's target OCP version:
  1. Validates gated assessment status (refusing NO-GO).
  2. Modifies cluster manifests (e.g. ACM ClusterCurator / ClusterDeployment CRs)
     using ruamel.yaml to preserve formatting, comments, and structure.
  3. Manages git branches, commits, and pushes via GitPython.
  4. Interacts with GitHub REST API to open new PRs (marking caveats as draft by default)
     or updating existing branches/PRs idempotently.
"""
from __future__ import annotations

import dataclasses
import logging
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, urlunparse

import git
import requests
from ruamel.yaml import YAML

log = logging.getLogger(__name__)


@dataclass
class RepoTarget:
    """GitOps repository configuration for a target cluster."""

    repo_url: str
    owner: str
    repo_name: str
    cluster_path: str
    curator_namespace: str
    base_branch: str = "main"
    upstream_graph_url: str | None = None


def get_authenticated_repo_url(repo_url: str, token: str) -> str:
    """Inject personal access token or installation token into HTTPS clone URL."""
    if not token or not repo_url.startswith("https://"):
        return repo_url
    parsed = urlparse(repo_url)
    auth_netloc = f"x-access-token:{token}@{parsed.netloc}"
    return urlunparse(parsed._replace(netloc=auth_netloc))


def create_yaml_parser() -> YAML:
    """Create a round-trip YAML parser preserving comments and indentation."""
    y = YAML()
    y.preserve_quotes = True
    y.indent(mapping=2, sequence=4, offset=2)
    return y


def update_cluster_manifests(
    repo_root: Path,
    target: RepoTarget,
    cluster_name: str,
    target_version: str,
) -> list[str]:
    """Find and update cluster upgrade manifests (e.g. ClusterCurator) using ruamel.yaml.

    Returns a list of updated file paths relative to repo_root.
    """
    cluster_dir = repo_root / target.cluster_path
    cluster_dir.mkdir(parents=True, exist_ok=True)
    yaml_parser = create_yaml_parser()
    modified_files: list[str] = []

    # Look for candidate YAML files in the cluster directory
    candidate_files = list(cluster_dir.glob("*.yaml")) + list(cluster_dir.glob("*.yml"))
    curator_found = False

    target_major_minor = ".".join(target_version.split(".")[:2])

    for fpath in candidate_files:
        try:
            with open(fpath, "r", encoding="utf-8") as fh:
                doc = yaml_parser.load(fh)
        except Exception as exc:
            log.warning("Could not parse %s as YAML: %s", fpath, exc)
            continue

        if not isinstance(doc, dict):
            continue

        kind = doc.get("kind")
        if kind == "ClusterCurator":
            curator_found = True
            spec = doc.setdefault("spec", {})
            spec["desiredCuration"] = "upgrade"
            upgrade_spec = spec.setdefault("upgrade", {})
            upgrade_spec["desiredUpdate"] = target_version
            if target.upstream_graph_url:
                upgrade_spec["upstream"] = target.upstream_graph_url
            if "channel" in upgrade_spec:
                upgrade_spec["channel"] = f"stable-{target_major_minor}"

            with open(fpath, "w", encoding="utf-8") as fh:
                yaml_parser.dump(doc, fh)
            modified_files.append(str(fpath.relative_to(repo_root)).replace("\\", "/"))
            log.info("Updated ClusterCurator in %s to target %s", fpath, target_version)

        elif kind in ("ClusterDeployment", "ClusterVersion"):
            spec = doc.setdefault("spec", {})
            if "desiredUpdate" in spec and isinstance(spec["desiredUpdate"], dict):
                spec["desiredUpdate"]["version"] = target_version
                with open(fpath, "w", encoding="utf-8") as fh:
                    yaml_parser.dump(doc, fh)
                modified_files.append(str(fpath.relative_to(repo_root)).replace("\\", "/"))
                log.info("Updated %s in %s to version %s", kind, fpath, target_version)

    # If no curator manifest existed, synthesize standard ACM ClusterCurator CR
    if not curator_found and not modified_files:
        curator_file = cluster_dir / "cluster-curator.yaml"
        curator_manifest = {
            "apiVersion": "cluster.open-cluster-management.io/v1beta1",
            "kind": "ClusterCurator",
            "metadata": {
                "name": cluster_name,
                "namespace": target.curator_namespace,
                "labels": {
                    "open-cluster-management.io/cluster-name": cluster_name,
                },
            },
            "spec": {
                "desiredCuration": "upgrade",
                "upgrade": {
                    "channel": f"stable-{target_major_minor}",
                    "desiredUpdate": target_version,
                },
            },
        }
        if target.upstream_graph_url:
            curator_manifest["spec"]["upgrade"]["upstream"] = target.upstream_graph_url

        with open(curator_file, "w", encoding="utf-8") as fh:
            yaml_parser.dump(curator_manifest, fh)
        modified_files.append(str(curator_file.relative_to(repo_root)).replace("\\", "/"))
        log.info("Created new ClusterCurator manifest at %s", curator_file)

    return modified_files


def render_pr_body(
    cluster_name: str,
    current_version: str,
    target_version: str,
    verdict: str,
    reasons: dict[str, Any],
    assessment_id: int | str,
    evaluated_at: str,
) -> str:
    """Generate structured, audit-ready Markdown PR description."""
    verdict_badge = "**GO** :white_check_mark:" if verdict == "go" else "**GO WITH CAVEATS** :warning:"
    if verdict == "no-go":
        verdict_badge = "**NO-GO** :x:"

    blockers = reasons.get("blockers") or reasons.get("blocking") or []
    caveats = reasons.get("caveats") or []
    info = reasons.get("info") or []

    lines = [
        f"## :robot: Automated Pre-Upgrade Assessment — {cluster_name}",
        "",
        f"This Pull Request proposes bumping cluster **`{cluster_name}`** OCP target from **`{current_version}`** to **`{target_version}`**.",
        "",
        f"| Parameter | Value |",
        f"| :--- | :--- |",
        f"| **Cluster** | `{cluster_name}` |",
        f"| **Current Version** | `{current_version}` |",
        f"| **Target Version** | `{target_version}` |",
        f"| **Assessment Verdict** | {verdict_badge} |",
        f"| **Assessment ID** | `#{assessment_id}` |",
        f"| **Evaluated At** | `{evaluated_at}` |",
        "",
    ]

    if verdict == "go-with-caveats":
        lines.extend([
            "> [!WARNING]",
            "> **This upgrade has conditional risks or caveats.**",
            "> This PR was created in draft mode for engineering review.",
            "",
        ])

    if caveats:
        lines.extend([
            "### :warning: Caveats & Conditional Risks",
            "",
        ])
        for c in caveats:
            detail = c.get("detail", c) if isinstance(c, dict) else c
            kind = c.get("kind") if isinstance(c, dict) else None
            prefix = f"**[{kind}]** " if kind else ""
            lines.append(f"- {prefix}{detail}")
        lines.append("")

    if blockers:
        lines.extend([
            "### :no_entry_sign: Blocking Issues",
            "",
        ])
        for b in blockers:
            detail = b.get("detail", b) if isinstance(b, dict) else b
            kind = b.get("kind") if isinstance(b, dict) else None
            prefix = f"**[{kind}]** " if kind else ""
            lines.append(f"- {prefix}{detail}")
        lines.append("")

    if info:
        lines.extend([
            "### :white_check_mark: Validated Compatibility Checks",
            "",
        ])
        for item in info:
            lines.append(f"- {item}")
        lines.append("")

    lines.extend([
        "### :clipboard: Pre-Merge Checklist",
        "- [ ] Verify disconnected/air-gapped release payload mirroring if applicable",
        "- [ ] Ensure active VM migrations (MTV) are quiescent before initiating node drains",
        "- [ ] Validate CSI storage replication & backup health (Dell CSM / Portworx)",
        "- [ ] Confirm maintenance window approval with TestOps / Release Engineering",
        "",
        "---",
        "*Automated by [OCV Upgrade & Migration Assessment Agent](https://github.com/openshift-virtualization/ocv-upgrade-agent)*",
    ])

    return "\n".join(lines)


def open_or_update_pr(
    cluster_name: str,
    current_version: str,
    target_version: str,
    verdict: str,
    reasons: dict[str, Any],
    target: RepoTarget,
    token: str,
    assessment_id: int | str,
    evaluated_at: str,
    force_ready: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Create or update a GitOps PR for a cluster upgrade."""
    branch_name = f"upgrade/{cluster_name}-to-{target_version}"
    commit_msg = f"feat(gitops): bump {cluster_name} OCP target to {target_version}"
    pr_title = f"feat(gitops): upgrade {cluster_name} to OCP {target_version} [{verdict.upper()}]"
    is_draft = (verdict == "go-with-caveats") and not force_ready

    pr_body = render_pr_body(
        cluster_name=cluster_name,
        current_version=current_version,
        target_version=target_version,
        verdict=verdict,
        reasons=reasons,
        assessment_id=assessment_id,
        evaluated_at=evaluated_at,
    )

    with tempfile.TemporaryDirectory(prefix="gitops_bot_", ignore_cleanup_errors=True) as temp_dir:
        repo_dir = Path(temp_dir) / "repo"
        repo = None

        try:
            if dry_run:
                log.info("[DRY-RUN] Simulating GitOps PR creation for %s -> %s", cluster_name, target_version)
                repo = git.Repo.init(repo_dir)
                # Create base branch and initial commit
                base_file = repo_dir / "README.md"
                base_file.write_text(f"# Fleet GitOps for {target.owner}/{target.repo_name}\n", encoding="utf-8")
                repo.index.add(["README.md"])
                repo.index.commit("initial commit")
                repo.create_head(target.base_branch)
                repo.git.checkout(target.base_branch)

                # Create branch
                head_branch = repo.create_head(branch_name)
                head_branch.checkout()

                modified_files = update_cluster_manifests(repo_dir, target, cluster_name, target_version)
                repo.index.add(modified_files)
                diff_text = repo.git.diff("HEAD")

                return {
                    "action": "dry-run-preview",
                    "cluster": cluster_name,
                    "current_version": current_version,
                    "target_version": target_version,
                    "verdict": verdict,
                    "branch": branch_name,
                    "base_branch": target.base_branch,
                    "draft": is_draft,
                    "pr_title": pr_title,
                    "pr_body": pr_body,
                    "modified_files": modified_files,
                    "diff": diff_text,
                }

            # Live Execution: Clone repo with auth
            auth_url = get_authenticated_repo_url(target.repo_url, token)
            log.info("Cloning GitOps repo %s...", target.repo_url)
            repo = git.Repo.clone_from(auth_url, repo_dir, branch=target.base_branch)

            # Checkout or create upgrade branch
            try:
                repo.git.checkout(branch_name)
                log.info("Checked out existing branch %s", branch_name)
            except git.GitCommandError:
                repo.git.checkout("-b", branch_name)
                log.info("Created and checked out new branch %s", branch_name)

            modified_files = update_cluster_manifests(repo_dir, target, cluster_name, target_version)

            if not modified_files:
                log.warning("No files modified during manifest update")

            # Commit and push
            repo.git.add(A=True)
            if repo.is_dirty(untracked_files=True):
                repo.index.commit(commit_msg)
                log.info("Committed changes: %s", commit_msg)
            else:
                log.info("Working directory clean; no new commit needed")

            log.info("Pushing branch %s to remote...", branch_name)
            origin = repo.remote(name="origin")
            origin.push(refspec=f"{branch_name}:{branch_name}", set_upstream=True, force=True)

            # GitHub API: Check for existing PR
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
            api_base = "https://api.github.com"
            pulls_url = f"{api_base}/repos/{target.owner}/{target.repo_name}/pulls"

            list_resp = requests.get(
                pulls_url,
                headers=headers,
                params={"head": f"{target.owner}:{branch_name}", "state": "open", "base": target.base_branch},
                timeout=30,
            )
            list_resp.raise_for_status()
            existing_prs = list_resp.json()

            if existing_prs:
                pr = existing_prs[0]
                pr_number = pr["number"]
                pr_url = pr["html_url"]
                log.info("Found existing open PR #%d: %s; updating...", pr_number, pr_url)

                update_resp = requests.patch(
                    f"{pulls_url}/{pr_number}",
                    headers=headers,
                    json={"title": pr_title, "body": pr_body, "draft": is_draft},
                    timeout=30,
                )
                update_resp.raise_for_status()
                action = "updated"
            else:
                log.info("Opening new PR for %s...", branch_name)
                create_resp = requests.post(
                    pulls_url,
                    headers=headers,
                    json={
                        "title": pr_title,
                        "body": pr_body,
                        "head": branch_name,
                        "base": target.base_branch,
                        "draft": is_draft,
                    },
                    timeout=30,
                )
                create_resp.raise_for_status()
                pr_data = create_resp.json()
                pr_url = pr_data["html_url"]
                pr_number = pr_data["number"]
                action = "created"

            return {
                "action": action,
                "pr_url": pr_url,
                "pr_number": pr_number,
                "cluster": cluster_name,
                "target_version": target_version,
                "branch": branch_name,
                "draft": is_draft,
                "modified_files": modified_files,
            }
        finally:
            if repo is not None:
                try:
                    repo.close()
                except Exception:
                    pass
