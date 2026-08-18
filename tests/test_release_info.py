from collectors.release_info import (
    _build_mirror_flags,
    parse_release_images,
    upsert_release_images,
)
from db.models import ReleaseImage
from tests.utils import load_fixture


def test_build_mirror_flags():
    flags = _build_mirror_flags(
        pull_secret="/path/to/pull-secret.json",
        icsp_file="/path/to/icsp.yaml",
        idms_file="/path/to/idms.yaml",
    )
    assert flags == [
        "-a",
        "/path/to/pull-secret.json",
        "--icsp-file=/path/to/icsp.yaml",
        "--idms-file=/path/to/idms.yaml",
    ]


def test_parse_release_images():
    metadata = load_fixture("sample_release_info.json")
    rows = parse_release_images(metadata)
    assert len(rows) == 2
    names = {r["component"] for r in rows}
    assert names == {"cluster-version-operator", "kubevirt-hyperconverged-operator"}
    assert all(r["version"] == "4.22.8" for r in rows)


def test_upsert(db_session):
    metadata = load_fixture("sample_release_info.json")
    rows = parse_release_images(metadata)
    n = upsert_release_images(db_session, rows)
    db_session.commit()
    assert n == 2
    assert db_session.query(ReleaseImage).count() == 2

