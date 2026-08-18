"""HashiCorp Vault Client for dynamic secret and cluster credential retrieval.

Provides secure fetching of:
1. Container registry mirror pull secrets (.dockerconfigjson).
2. Per-cluster login credentials (kubeconfig YAML, bearer tokens).

Supports Token and AppRole authentication with KV v1 and KV v2 secret engines.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any

import requests

log = logging.getLogger(__name__)

DEFAULT_VAULT_ADDR = "http://127.0.0.1:8200"


class VaultClient:
    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        role_id: str | None = None,
        secret_id: str | None = None,
        namespace: str | None = None,
        session: requests.Session | None = None,
        timeout: int = 15,
    ):
        self.base_url = (base_url or os.environ.get("VAULT_ADDR", DEFAULT_VAULT_ADDR)).rstrip("/")
        self.token = token or os.environ.get("VAULT_TOKEN")
        self.role_id = role_id or os.environ.get("VAULT_ROLE_ID")
        self.secret_id = secret_id or os.environ.get("VAULT_SECRET_ID")
        self.namespace = namespace or os.environ.get("VAULT_NAMESPACE")
        self.http = session or requests.Session()
        self.timeout = timeout

        if not self.token and self.role_id and self.secret_id:
            self._login_approle()

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.token:
            headers["X-Vault-Token"] = self.token
        if self.namespace:
            headers["X-Vault-Namespace"] = self.namespace
        return headers

    def _login_approle(self) -> None:
        """Authenticate using AppRole role_id and secret_id."""
        url = f"{self.base_url}/v1/auth/approle/login"
        payload = {"role_id": self.role_id, "secret_id": self.secret_id}
        try:
            resp = self.http.post(url, json=payload, headers=self._headers(), timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            client_token = data.get("auth", {}).get("client_token")
            if client_token:
                self.token = client_token
                log.info("Successfully authenticated with Vault AppRole")
        except Exception as exc:
            log.warning("Vault AppRole authentication failed: %s", exc)

    def read_secret(self, path: str) -> dict[str, Any]:
        """Read secret from Vault KV engine (handles both KV v1 and KV v2)."""
        clean_path = path.lstrip("/")
        if not clean_path.startswith("v1/"):
            url = f"{self.base_url}/v1/{clean_path}"
        else:
            url = f"{self.base_url}/{clean_path}"

        resp = self.http.get(url, headers=self._headers(), timeout=self.timeout)
        resp.raise_for_status()
        payload = resp.json()

        # Handle KV v2 structure: data.data
        if "data" in payload and isinstance(payload["data"], dict) and "data" in payload["data"]:
            return payload["data"]["data"]
        # Handle KV v1 structure: data
        if "data" in payload and isinstance(payload["data"], dict):
            return payload["data"]
        return payload

    def get_pull_secret(self, secret_path: str = "secret/data/registry/pull-secret") -> str | None:
        """Retrieve registry pull secret string/JSON from Vault."""
        try:
            data = self.read_secret(secret_path)
            if not data:
                return None
            # Common keys for pull secrets
            for key in (".dockerconfigjson", "pull_secret", "pullSecret", "auths", "config.json"):
                if key in data:
                    val = data[key]
                    return json.dumps(val) if isinstance(val, dict) else str(val)
            # If the secret payload itself is the auth dict
            return json.dumps(data)
        except Exception as exc:
            log.warning("Failed to fetch pull secret from Vault path %s: %s", secret_path, exc)
            return None

    def get_cluster_credentials(
        self, cluster_name: str, template: str = "secret/data/clusters/{cluster}"
    ) -> dict[str, Any] | None:
        """Retrieve cluster ServiceAccount credentials from Vault."""
        path = template.format(cluster=cluster_name)
        try:
            data = self.read_secret(path)
            if not data:
                return None
            return data
        except Exception as exc:
            log.warning("Failed to fetch ServiceAccount credentials for %s from Vault (%s): %s", cluster_name, path, exc)
            return None

    def get_cluster_kubeconfig(
        self,
        cluster_name: str,
        template: str = "secret/data/clusters/{cluster}",
        fallback_api_url: str | None = None,
    ) -> str | None:
        """Retrieve or dynamically synthesize kubeconfig YAML from Vault ServiceAccount credentials."""
        creds = self.get_cluster_credentials(cluster_name, template=template)
        if not creds:
            return None

        # 1. If the secret already contains a full kubeconfig file string
        for key in ("kubeconfig", "config"):
            if key in creds and "apiVersion" in str(creds[key]):
                return str(creds[key])

        # 2. Extract ServiceAccount token and server endpoint
        token = creds.get("token") or creds.get("bearer_token") or creds.get("sa_token") or creds.get("password")
        api_url = creds.get("api_url") or creds.get("server") or creds.get("endpoint") or fallback_api_url
        ca_cert = creds.get("ca_cert") or creds.get("ca.crt") or creds.get("certificate_authority_data")
        insecure = creds.get("insecure_skip_tls_verify", True)

        if not token or not api_url:
            log.warning("Incomplete ServiceAccount credentials for %s in Vault (need token and api_url)", cluster_name)
            return None

        # 3. Synthesize valid standalone Kubeconfig YAML for Kubernetes client
        import base64

        cluster_entry: dict[str, Any] = {"server": api_url}
        if ca_cert:
            clean_ca = ca_cert.strip()
            if not clean_ca.startswith("-----BEGIN"):
                cluster_entry["certificate-authority-data"] = clean_ca
            else:
                cluster_entry["certificate-authority-data"] = base64.b64encode(clean_ca.encode()).decode()
        else:
            cluster_entry["insecure-skip-tls-verify"] = insecure

        kubeconfig_dict = {
            "apiVersion": "v1",
            "kind": "Config",
            "clusters": [
                {
                    "name": cluster_name,
                    "cluster": cluster_entry,
                }
            ],
            "contexts": [
                {
                    "name": cluster_name,
                    "context": {
                        "cluster": cluster_name,
                        "user": f"sa-{cluster_name}",
                    },
                }
            ],
            "current-context": cluster_name,
            "users": [
                {
                    "name": f"sa-{cluster_name}",
                    "user": {"token": str(token).strip()},
                }
            ],
        }

        import yaml
        return yaml.dump(kubeconfig_dict)

    def get_llm_credentials(self, secret_path: str = "secret/data/llm") -> dict[str, str]:
        """Retrieve LLM API key, endpoint URL, and model from Vault."""
        try:
            data = self.read_secret(secret_path)
            if not data:
                return {}
            return {
                "api_key": data.get("api_key") or data.get("token") or data.get("apiKey") or "",
                "base_url": data.get("base_url") or data.get("url") or data.get("endpoint") or "",
                "model": data.get("model") or data.get("model_name") or "",
            }
        except Exception as exc:
            log.warning("Failed to fetch LLM credentials from Vault path %s: %s", secret_path, exc)
            return {}


