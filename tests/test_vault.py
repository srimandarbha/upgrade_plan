from unittest.mock import MagicMock, patch
import json
import pytest

from vault.client import VaultClient


def test_vault_approle_login():
    mock_session = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"auth": {"client_token": "s.vault-test-token-12345"}}
    mock_session.post.return_value = mock_resp

    client = VaultClient(
        base_url="https://vault.internal.net:8200",
        role_id="test-role-id",
        secret_id="test-secret-id",
        session=mock_session,
    )
    assert client.token == "s.vault-test-token-12345"


def test_vault_read_secret_kv2():
    mock_session = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "data": {
            "data": {
                ".dockerconfigjson": '{"auths":{"registry.local":{"auth":"dXNlcjpwYXNz"}}}'
            }
        }
    }
    mock_session.get.return_value = mock_resp

    client = VaultClient(
        base_url="https://vault.internal.net:8200",
        token="s.test-token",
        session=mock_session,
    )
    pull_secret = client.get_pull_secret("secret/data/registry/pull-secret")
    assert "registry.local" in pull_secret


def test_vault_get_cluster_kubeconfig_direct():
    mock_session = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "data": {
            "data": {
                "kubeconfig": "apiVersion: v1\nclusters:\n- cluster:\n    server: https://api.east-prod-01.k8s:6443"
            }
        }
    }
    mock_session.get.return_value = mock_resp

    client = VaultClient(
        base_url="https://vault.internal.net:8200",
        token="s.test-token",
        session=mock_session,
    )
    kubeconfig = client.get_cluster_kubeconfig("east-prod-01")
    assert "api.east-prod-01.k8s:6443" in kubeconfig


def test_vault_get_cluster_from_service_account_credentials():
    mock_session = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "data": {
            "data": {
                "token": "eyJhbGciOiJSUzI1NiIs...",
                "server": "https://api.west-prod-02.example.com:6443",
                "insecure_skip_tls_verify": True,
            }
        }
    }
    mock_session.get.return_value = mock_resp

    client = VaultClient(
        base_url="https://vault.internal.net:8200",
        token="s.test-token",
        session=mock_session,
    )
    kubeconfig = client.get_cluster_kubeconfig("west-prod-02")
    assert kubeconfig is not None
    assert "https://api.west-prod-02.example.com:6443" in kubeconfig
    assert "eyJhbGciOiJSUzI1NiIs..." in kubeconfig

