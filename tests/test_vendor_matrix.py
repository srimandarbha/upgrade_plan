from pathlib import Path

from collectors.vendor_matrix import collect, load_seed
from db.models import Advisory, OperatorCompat

SEED = Path(__file__).resolve().parents[1] / "data" / "vendor_matrix_seed.yaml"


def test_load_seed_shape():
    data = load_seed(SEED)
    assert len(data["operator_compat"]) >= 2
    assert len(data["known_bugs"]) >= 1
    assert data["known_bugs"][0]["external_id"] == "PWX-46691"


def test_collect_writes_both_tables(db_session):
    n_compat, n_bugs = collect(SEED)
    assert n_compat >= 2
    assert n_bugs >= 1
    assert db_session.query(OperatorCompat).filter_by(component="dell-csm").count() == 1
    assert db_session.query(Advisory).filter_by(source="portworx", external_id="PWX-46691").count() == 1
