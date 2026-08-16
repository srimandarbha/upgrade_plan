import datetime

from collectors.lifecycle import _parse_item, upsert_lifecycle
from db.models import ProductLifecycle
from tests.utils import load_fixture


def test_parse_item_maps_named_phases_to_columns():
    data = load_fixture("sample_lifecycle.json")
    row = _parse_item(data["data"][1], "ocp")
    assert row["version"] == "4.22"
    assert row["ga_date"] == datetime.date(2026, 6, 9)
    assert row["full_support_end"] == datetime.date(2026, 6, 9)
    assert row["maintenance_end"] == datetime.date(2027, 12, 9)
    assert row["eol_date"] == datetime.date(2028, 6, 9)


def test_upsert(db_session):
    data = load_fixture("sample_lifecycle.json")
    rows = [_parse_item(i, "ocp") for i in data["data"]]
    n = upsert_lifecycle(db_session, rows)
    db_session.commit()
    assert n == 2
    assert db_session.query(ProductLifecycle).count() == 2
