from collectors.cincinnati import parse_edges, upsert_edges
from db.models import UpgradeEdge
from tests.utils import load_fixture


def test_parse_edges_splits_unconditional_and_conditional():
    graph = load_fixture("sample_cincinnati_graph.json")
    rows = parse_edges(graph, channel="stable-4.22", arch="amd64")

    unconditional = [r for r in rows if not r["conditional"]]
    conditional = [r for r in rows if r["conditional"]]
    assert len(unconditional) == 3
    assert len(conditional) == 1

    risk = conditional[0]
    assert (risk["from_version"], risk["to_version"]) == ("4.21.22", "4.22.6")
    assert risk["risk_name"] == "MultipathSCSIQueueDepth"
    assert risk["matching_rule"][0]["type"] == "PromQL"


def test_upsert(db_session):
    graph = load_fixture("sample_cincinnati_graph.json")
    rows = parse_edges(graph, channel="stable-4.22", arch="amd64")
    n = upsert_edges(db_session, rows)
    db_session.commit()
    assert n == 4
    assert db_session.query(UpgradeEdge).count() == 4
