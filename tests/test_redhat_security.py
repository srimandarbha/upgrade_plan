from collectors.redhat_security import _parse_cve_item, _parse_csaf_item, upsert_advisories
from db.models import Advisory
from tests.utils import load_fixture


def test_parse_cve_item():
    items = load_fixture("sample_cve.json")
    row = _parse_cve_item(items[0], "ocp")
    assert row["source"] == "redhat-cve"
    assert row["external_id"] == "CVE-2026-31431"
    assert row["severity"] == "important"
    assert row["affected_component"] == "ocp"
    assert row["published_at"].year == 2026
    assert row["url"].endswith("CVE-2026-31431.json")


def test_parse_csaf_item():
    items = load_fixture("sample_csaf.json")
    row = _parse_csaf_item(items[0], "ocp")
    assert row["source"] == "redhat-errata"
    assert row["external_id"] == "RHSA-2026:29834"
    assert row["severity"] == "important"


def test_upsert_then_reupsert_updates_in_place(db_session):
    items = load_fixture("sample_cve.json")
    rows = [_parse_cve_item(i, "ocp") for i in items]

    n = upsert_advisories(db_session, rows)
    db_session.commit()
    assert n == 2
    assert db_session.query(Advisory).count() == 2

    rows[0]["severity"] = "critical"
    upsert_advisories(db_session, rows)
    db_session.commit()

    assert db_session.query(Advisory).count() == 2  # no duplicate row
    updated = db_session.query(Advisory).filter_by(external_id="CVE-2026-31431").one()
    assert updated.severity == "critical"
