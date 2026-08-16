"""Cincinnati/OSUS graph collector -> upgrade_edges table.

Public endpoint (bastion use):
    https://api.openshift.com/api/upgrades_info/v1/graph?channel=stable-4.22&arch=amd64
    (requires `Accept: application/json`)

Disconnected/local OSUS (real fleet use -- get the base URL with):
    oc -n openshift-update-service get updateservice/osus \\
        -o jsonpath='{.status.policyEngineURI}'

Point CINCINNATI_URL at whichever one applies; this module doesn't care which,
it just needs a base URL that serves the same `/api/upgrades_info/v1/graph`
contract. Querying your own OSUS is what you want for the graph shape that
actually reflects your mirrored release set.

Graph shape: {"nodes": [...], "edges": [[i, j], ...], "conditionalEdges": [...]}
`edges` are unconditional (index pairs into `nodes`); `conditionalEdges` carry
a `risks` list, each with a human-readable message and a PromQL matchingRule
-- this is reference data (which risks exist for this edge), not a verdict for
any specific cluster. For "does this risk actually apply to *my* cluster",
read the live ClusterVersion object instead -- see cluster_state.py.
"""
from __future__ import annotations

import argparse
import logging
import os

import requests
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from db.db import get_session
from db.models import UpgradeEdge

log = logging.getLogger(__name__)

PUBLIC_CINCINNATI_URL = "https://api.openshift.com"
DEFAULT_CHANNELS = ["stable-4.21", "stable-4.22"]


def fetch_graph(
    channel: str,
    arch: str = "amd64",
    base_url: str | None = None,
    session: requests.Session | None = None,
) -> dict:
    base_url = base_url or os.environ.get("CINCINNATI_URL", PUBLIC_CINCINNATI_URL)
    http = session or requests
    resp = http.get(
        f"{base_url.rstrip('/')}/api/upgrades_info/v1/graph",
        params={"channel": channel, "arch": arch},
        headers={"Accept": "application/json"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def parse_edges(graph: dict, channel: str, arch: str) -> list[dict]:
    nodes = graph.get("nodes", [])
    versions = [n.get("version") for n in nodes]
    rows: list[dict] = []

    for pair in graph.get("edges", []):
        if len(pair) != 2:
            continue
        i, j = pair
        if i >= len(versions) or j >= len(versions):
            continue
        rows.append(
            {
                "channel": channel,
                "arch": arch,
                "from_version": versions[i],
                "to_version": versions[j],
                "conditional": False,
                "risk_name": None,
                "risk_message": None,
                "matching_rule": None,
            }
        )

    for cond in graph.get("conditionalEdges", []):
        edges = cond.get("edges", [])
        risks = cond.get("risks", [])
        for edge in edges:
            frm, to = edge.get("from"), edge.get("to")
            if not risks:
                rows.append(
                    {
                        "channel": channel,
                        "arch": arch,
                        "from_version": frm,
                        "to_version": to,
                        "conditional": True,
                        "risk_name": None,
                        "risk_message": None,
                        "matching_rule": None,
                    }
                )
            for risk in risks:
                rows.append(
                    {
                        "channel": channel,
                        "arch": arch,
                        "from_version": frm,
                        "to_version": to,
                        "conditional": True,
                        "risk_name": risk.get("name"),
                        "risk_message": risk.get("message"),
                        "matching_rule": risk.get("matchingRules"),
                    }
                )
    return rows


def upsert_edges(session: Session, rows: list[dict]) -> int:
    if not rows:
        return 0
    dialect = session.get_bind().dialect.name
    insert_fn = pg_insert if dialect == "postgresql" else sqlite_insert
    stmt = insert_fn(UpgradeEdge).values(rows)
    update_cols = {
        c: getattr(stmt.excluded, c)
        for c in rows[0]
        if c not in ("channel", "arch", "from_version", "to_version", "risk_name")
    }
    stmt = stmt.on_conflict_do_update(
        index_elements=["channel", "arch", "from_version", "to_version", "risk_name"],
        set_=update_cols,
    )
    session.execute(stmt)
    return len(rows)


def collect(channels: list[str] | None = None, arch: str = "amd64", base_url: str | None = None) -> int:
    channels = channels or DEFAULT_CHANNELS
    total = 0
    with get_session() as db:
        for channel in channels:
            try:
                graph = fetch_graph(channel, arch=arch, base_url=base_url)
            except requests.RequestException as exc:
                log.warning("Graph fetch failed for channel %s: %s", channel, exc)
                continue
            rows = parse_edges(graph, channel, arch)
            total += upsert_edges(db, rows)
    return total


def main():
    logging.basicConfig(level=logging.INFO)
    ap = argparse.ArgumentParser(description="Pull the Cincinnati/OSUS upgrade graph")
    ap.add_argument("--channel", action="append", help="repeatable, e.g. stable-4.22")
    ap.add_argument("--arch", default="amd64")
    ap.add_argument("--base-url", help="defaults to $CINCINNATI_URL, then the public API")
    args = ap.parse_args()
    n = collect(channels=args.channel, arch=args.arch, base_url=args.base_url)
    log.info("Upserted %d upgrade edges", n)


if __name__ == "__main__":
    main()
