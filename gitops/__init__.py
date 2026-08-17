"""GitOps automation bot for OpenShift / OCV fleet upgrades."""
from __future__ import annotations

from gitops.bot import RepoTarget, open_or_update_pr

__all__ = ["RepoTarget", "open_or_update_pr"]
