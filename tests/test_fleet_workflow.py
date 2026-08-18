import os
from unittest.mock import patch

from run_fleet_workflow import configure_proxy, run_fleet_pipeline


def test_configure_proxy():
    configure_proxy(
        http_proxy="http://proxy.corp.net:8080",
        https_proxy="http://proxy.corp.net:8443",
        no_proxy="localhost,127.0.0.1,.corp.net",
    )
    assert os.environ["HTTP_PROXY"] == "http://proxy.corp.net:8080"
    assert os.environ["HTTPS_PROXY"] == "http://proxy.corp.net:8443"
    assert os.environ["NO_PROXY"] == "localhost,127.0.0.1,.corp.net"


def test_run_fleet_pipeline_prod_and_lab(db_session):
    from db.models import Cluster
    db_session.add(Cluster(name="test-prod-01", env="prod", region="us-east-1", ocp_version="4.20.0"))
    db_session.add(Cluster(name="test-lab-01", env="lab", region="us-east-1", ocp_version="4.20.0"))
    db_session.commit()


    # Assess Prod only
    prod_res = run_fleet_pipeline(
        target_version="4.22.8",
        env="prod",
        skip_gitops_sync=True,
        enable_testops=False,
    )
    assert len(prod_res["clusters"]) == 1
    assert prod_res["clusters"][0]["cluster"] == "test-prod-01"

    # Assess Lab only
    lab_res = run_fleet_pipeline(
        target_version="4.22.8",
        env="lab",
        skip_gitops_sync=True,
        enable_testops=False,
    )
    assert len(lab_res["clusters"]) == 1
    assert lab_res["clusters"][0]["cluster"] == "test-lab-01"
