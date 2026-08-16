from collectors.cluster_state import parse_clusterversion, parse_csvs
from tests.utils import load_fixture


def test_parse_clusterversion_surfaces_conditional_risks():
    cv = load_fixture("sample_clusterversion.json")
    result = parse_clusterversion(cv)
    assert result["version"] == "4.21.22"
    assert result["channel"] == "stable-4.21"
    assert len(result["available_updates"]) == 1
    assert len(result["conditional_updates"]) == 1
    assert result["conditional_updates"][0]["risks"][0]["name"] == "MultipathSCSIQueueDepth"


def test_parse_csvs_matches_target_components_and_skips_others():
    csvs = load_fixture("sample_csvs.json")
    rows = parse_csvs(csvs)

    components = {r["component"] for r in rows}
    assert components == {"ocv", "dell-csm", "portworx"}
    assert len(rows) == 3  # cert-manager ignored, Failed-phase operator skipped

    ocv_row = next(r for r in rows if r["component"] == "ocv")
    assert ocv_row["version"] == "4.21.3"
    assert ocv_row["namespace"] == "openshift-cnv"
    assert ocv_row["csv_name"] == "kubevirt-hyperconverged-operator.v4.21.3"

    csm_row = next(r for r in rows if r["component"] == "dell-csm")
    assert csm_row["version"] == "1.9.2"
