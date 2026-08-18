import json
from pathlib import Path

from collectors.redhat_security import (
    classify_component,
    collect,
    parse_csaf_document,
    upsert_advisories,
)
from db.models import Advisory


def test_classify_component():
    assert classify_component("Red Hat OpenShift Virtualization 4.22") == "ocv"
    assert classify_component("Red Hat OpenShift Container Platform 4.22.8 CoreOS") == "ocp"
    assert classify_component("Red Hat Satellite 6.14 Server") is None


def test_parse_csaf_document_advisory():
    doc = {
        "document": {
            "category": "csaf_security_advisory",
            "title": "Important: Red Hat OpenShift Virtualization 4.21.0 security update",
            "tracking": {
                "id": "RHSA-2026:29834",
                "current_release_date": "2026-07-10T00:00:00Z",
            },
            "aggregate_severity": {"text": "Important"},
        },
        "vulnerabilities": [
            {
                "cve": "CVE-2026-31431",
                "title": "vhost-user-blk memory corruption in kubevirt",
                "scores": [{"cvss_v3": {"baseSeverity": "IMPORTANT"}}],
            }
        ],
    }

    rows = parse_csaf_document(doc)
    assert len(rows) == 2

    rhsa_row = next(r for r in rows if r["external_id"] == "RHSA-2026:29834")
    assert rhsa_row["source"] == "redhat-errata"
    assert rhsa_row["severity"] == "important"
    assert rhsa_row["affected_component"] == "ocv"
    assert rhsa_row["published_at"].year == 2026

    cve_row = next(r for r in rows if r["external_id"] == "CVE-2026-31431")
    assert cve_row["source"] == "redhat-cve"
    assert cve_row["severity"] == "important"
    assert cve_row["affected_component"] == "ocv"


def test_upsert_and_offline_directory_loading(db_session, tmp_path):
    doc = {
        "document": {
            "category": "csaf_security_advisory",
            "title": "Moderate: OpenShift Container Platform 4.22.8 bug fix and security update",
            "tracking": {
                "id": "RHSA-2026:5520",
                "current_release_date": "2026-08-01T00:00:00Z",
            },
            "aggregate_severity": {"text": "Moderate"},
        }
    }

    # Save to tmp directory
    doc_file = tmp_path / "rhsa-2026-5520.json"
    doc_file.write_text(json.dumps(doc), encoding="utf-8")

    n = collect(csaf_dir=tmp_path)
    assert n == 1
    assert db_session.query(Advisory).filter_by(external_id="RHSA-2026:5520").count() == 1

    # Re-upsert with updated severity (in-place update)
    doc["document"]["aggregate_severity"]["text"] = "Critical"
    doc_file.write_text(json.dumps(doc), encoding="utf-8")
    collect(csaf_dir=tmp_path)

    updated = db_session.query(Advisory).filter_by(external_id="RHSA-2026:5520").one()
    assert updated.severity == "critical"

