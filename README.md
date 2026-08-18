# OCV Upgrade & Migration Assessment Agent

An automated, offline-first pre-upgrade assessment agent for disconnected and bare-metal **OpenShift Container Platform (OCP)** and **OpenShift Virtualization (OCV)** fleets.

It combines:
1. **Deterministic facts engine:** Ingests Red Hat CVEs, RHSAs, Cincinnati/OSUS upgrade graphs, and product lifecycle dates into PostgreSQL.
2. **Operator compatibility matrix:** Validates compatibility bounds for **MTV (Migration Toolkit for Virtualization / `forklift-operator`)**, **Dell CSM**, and **Portworx**.
3. **Strategic LLM & TestOps Advisor:** Enforces **TestOps Confluence migration policies** (e.g. `TESTOPS-POL-4082`), evaluates major version drift (e.g. OCP 4 $\rightarrow$ 5), and generates **NO-GO (ESCALATE)** reports with actionable remediation plans and human sign-off gates.

---

## Architecture Overview

```
                               ┌──────────────────────────────────────────────┐
                               │       Cluster Inventory & Target Version     │
                               └──────────────────────┬───────────────────────┘
                                                      │
                       ┌──────────────────────────────┼──────────────────────────────┐
                       ▼                              ▼                              ▼
          ┌─────────────────────────┐    ┌─────────────────────────┐    ┌─────────────────────────┐
          │  Deterministic Engine   │    │   Operator Matrices     │    │   TestOps Confluence    │
          │  • Cincinnati graph     │    │   • Dell CSM Matrix     │    │   • Migration Gates     │
          │  • CVE & RHSAs          │    │   • Portworx Matrix     │    │   • CSI Storage Tests   │
          │  • Support Lifecycles   │    │   • MTV (Forklift)      │    │   • Major Drift Rules   │
          └────────────┬────────────┘    └────────────┬────────────┘    └────────────┬────────────┘
                       │                              │                              │
                       └──────────────────────────────┼──────────────────────────────┘
                                                      │
                                                      ▼
                                ┌───────────────────────────────────────────┐
                                │   LLM Strategic Upgrade & Migration Agent │
                                │   • Drift & Risk Assessment (4.x -> 5.x)  │
                                │   • Migration Motive & Stability Analysis │
                                │   • Blocker & Escalation Decision Logic   │
                                └─────────────────────┬─────────────────────┘
                                                      │
                                                      ▼
                                ┌───────────────────────────────────────────┐
                                │   Structured Escalation & Action Report   │
                                │   1. Verdict (GO / NO-GO [ESCALATE])      │
                                │   2. Executive Synopsis & Risk Rationale  │
                                │   3. Deep Component & Storage Impact      │
                                │   4. Step-by-Step TestOps Remediation Plan│
                                │   5. Human-in-the-Loop Sign-off Gate      │
                                └───────────────────────────────────────────┘
```

---

## Directory Layout

```text
db/
  schema.sql                   Postgres DDL (source of truth for prod)
  postgres_seed_4.20_to_4.22.sql Complete PostgreSQL DDL + 4.20->4.22 seed dataset
  models.py                    SQLAlchemy models (PostgreSQL)
  db.py                        Engine & session factory, auto-loads .env
vault/
  client.py                    HashiCorp Vault client (Token/AppRole, KV v1/v2, SA synthesis)
collectors/
  redhat_security.py           CSAF v2 VEX (CVEs) + Advisories (RHSAs) -> advisories
  lifecycle.py                 GA/EOL dates      -> product_lifecycle
  cincinnati.py                OSUS upgrade graph-> upgrade_edges
  vendor_matrix.py             Dell/Portworx/MTV -> operator_compat
  cluster_state.py             Live cluster state (SA or kubeconfig) -> component_versions
  release_info.py              Mirrored payload images (ICSP/IDMS)   -> release_images
  gitops_inventory.py          redhat-cop GitOps template mapping   -> clusters & component_versions
scripts/
  load_postgres_seed.py        One-step loader for PostgreSQL disconnected DB seed
  bundle_project.py            Comprehensive project exporter / packager
gitops/
  bot.py                       GitOps PR automation, ruamel.yaml editing, GitPython & GitHub API
data/
  gitops_targets.yaml          Fleet GitOps repository targets and cluster curator mapping
  vendor_matrix_seed.yaml      Hand-curated MTV, Dell CSM, and Portworx compatibility matrix
  testops_confluence_policy.md Ingested TestOps Confluence standards & migration gates
engine/
  compatibility.py             Deterministic GO / GO-WITH-CAVEATS / NO-GO assessment engine
  llm_advisor.py               Strategic LLM & TestOps migration escalation advisor
run_collectors.py              Orchestrator for all data collectors (Vault / GitOps / Mirroring)
run_assessment.py              CLI entrypoint for 50+ cluster fleet upgrade assessments
run_gitops_pr.py               CLI entrypoint for opening/updating GitOps upgrade PRs
tests/                         Unit tests against saved fixtures (no live network needed)
```

---

## Secrets & Credentials Configuration (.env & HashiCorp Vault)

The agent supports two backends for all credentials: **local `.env` file** and **HashiCorp Vault** (AppRole or Token).

### 1. HashiCorp Vault Backend Setup
Configure your Vault connection in `.env`:
```env
VAULT_ADDR=https://vault.internal.net:8200
VAULT_NAMESPACE=admin/ocp-fleet

# Option A: Token Auth
VAULT_TOKEN=s.yourVaultTokenHere

# Option B: AppRole Auth
VAULT_ROLE_ID=your-approle-role-id
VAULT_SECRET_ID=your-approle-secret-id
```

### 2. LLM Credentials Resolution
Supports OpenAI-compatible LLM endpoints (llama.cpp, vLLM, Ollama, OpenAI, Azure):
* **Backend A (`.env` file):**
  ```env
  LLM_BASE_URL=http://127.0.0.1:8080/v1/chat/completions
  LLM_API_KEY=your-api-key-if-required
  LLM_MODEL=meta-llama/Llama-3-70B-Instruct
  ```
* **Backend B (HashiCorp Vault):**
  ```env
  VAULT_LLM_SECRET_PATH=secret/data/llm
  ```
  *(Vault secret JSON contains `{"base_url": "...", "api_key": "...", "model": "..."}`)*

### 3. Registry Mirror Pull Secrets Resolution
Used by `release-info` to inspect mirrored release payloads in air-gapped networks:
* **Backend A (`.env` or local path):**
  ```env
  PULL_SECRET_PATH=/etc/ocv-agent/mirror-pull-secret.json
  ```
* **Backend B (HashiCorp Vault):**
  ```env
  VAULT_PULL_SECRET_PATH=secret/data/registry/pull-secret
  ```

### 4. Cluster ServiceAccount User Credentials Resolution
Used for live cluster pre-upgrade inspections without static kubeconfig files:
* **Backend A (Multi-context Kubeconfig):**
  ```env
  KUBECONFIG=/etc/ocv-agent/kubeconfig
  ```
* **Backend B (HashiCorp Vault Dynamic ServiceAccount):**
  ```env
  VAULT_CLUSTER_CREDS_TEMPLATE=secret/data/clusters/{cluster}
  ```
  *(Vault secret JSON contains `{"token": "...", "server": "https://api...", "ca_cert": "..."}`)*


---

## End-to-End Fleet Workflow Wrapper (`run_fleet_workflow.py`)

The `run_fleet_workflow.py` wrapper orchestrates corporate proxy configuration, pulls latest GitOps changes from Lab/Prod repositories, and triggers assessments across targeted clusters with TestOps Confluence governance:

> [!IMPORTANT]
> **Production Policy Gate:** Confluence migration policy validation is **strictly mandatory for all Production clusters**. Disabling Confluence (`--disable-confluence`) or TestOps reasoning (`--disable-testops`) is only permitted for initial seed **Lab / Non-Prod** clusters to perform sandbox pre-qualification before scheduling production upgrade windows.

```bash
# 1. Evaluate Lab/Staging seed clusters (Confluence exclusion permitted for first-time seed qualification):
python run_fleet_workflow.py --env lab --target 4.22.8 --disable-confluence

# 2. Evaluate Production clusters through corporate proxy (Confluence & TestOps strictly enforced):
python run_fleet_workflow.py --env prod --target 4.22.8 \
  --https-proxy http://proxy.corp.net:8080 \
  --no-proxy localhost,127.0.0.1,.internal.net

# 3. Evaluate entire 50+ cluster fleet:
python run_fleet_workflow.py --env all --target 4.22.8
```


---

## Running Data Collectors

The `run_collectors.py` orchestrator populates your PostgreSQL database. You can run all collectors or select specific feeds:

### Collector Feeds & Target Tables Reference

| Collector Module | Source Data | Target Table | Network Requirement | What It Ingests |
| :--- | :--- | :--- | :--- | :--- |
| `gitops_inventory` | `redhat-cop` GitOps repository | `clusters`, `component_versions` | None (Local/Git) | Scans `clusters/<name>/` and `components/operators/` for `Subscription` CRDs (channel, startingCSV), mapping 50+ clusters. |
| `redhat_security` | `security.access.redhat.com/data/csaf/v2/` | `advisories` | Bastion (or offline `--csaf-dir`) | CSAF 2.0 VEX (CVEs) and Advisories (RHSAs, RHBAs, RHEAs) for OCP & OCV components. |
| `cincinnati` | OpenShift Update Service (OSUS) | `upgrade_edges` | Bastion or Disconnected OSUS route | Upgrade graph edges, blocked edges, and conditional update risk conditions. |
| `lifecycle` | Red Hat Product Life Cycle API | `product_lifecycle` | Bastion | GA and End-of-Life (EOL) dates for OpenShift and OpenShift Virtualization. |
| `vendor_matrix` | Verified matrix YAML (`data/vendor_matrix_seed.yaml`) | `operator_compat` | Local | Minimum and maximum supported OCP versions for **MTV (Forklift)**, **Dell CSM**, and **Portworx**. |
| `release_info` | Mirrored container payload (`oc adm release info`) | `release_images` | Disconnected (Registry Mirror) | Component image pullspecs and digests using `--icsp-file` / `--idms-file` and pull secrets. |
| `cluster_state` | Live Kubernetes CustomObjectsApi | `component_versions` | Disconnected (Cluster API) | Live fallback reading of `ClusterVersion` and healthy `ClusterServiceVersion` (CSVs) in `Succeeded` phase. |

### Collector Invocation Examples

```bash
# 1. Ingest 50+ cluster operator mappings from redhat-cop GitOps template repo:
python run_collectors.py --only gitops-inventory --gitops-dir /path/to/gitops-standards-repo

# 2. Ingest Red Hat CSAF v2 VEX & Advisories (online or offline directory):
python run_collectors.py --only redhat-security --csaf-dir /path/to/csaf-bundle/

# 3. Pull registry mirror secret from HashiCorp Vault and inspect release payload:
python run_collectors.py --only release-info \
  --release-version registry.local:5000/ocp-release:4.22.8-x86_64 \
  --vault-pull-secret-path secret/data/registry/pull-secret \
  --icsp-file=/path/to/icsp.yaml

# 4. Pull Cincinnati graph for a specific channel (e.g., stable-4.22):
python run_collectors.py --only cincinnati --channel stable-4.22

# 5. Ingest MTV, Dell CSM, and Portworx compatibility seed matrices:
python run_collectors.py --only vendor-matrix
```

---

## How Cluster & Operator Mapping Works

The agent maps your 50+ cluster fleet and installed operators using a two-tier approach:

### 1. Primary Mapping: GitOps Repository (`collectors/gitops_inventory.py`)
In enterprise disconnected environments, live network access to 50+ clusters simultaneously is often restricted. The agent crawls your GitOps repository ([`redhat-cop/gitops-standards-repo-template`](https://github.com/redhat-cop/gitops-standards-repo-template)):
1. **Cluster Declarations:** Discovers cluster names and target versions from `clusters/<cluster_name>/` manifests (`ClusterCurator`, `ClusterDeployment`, `kustomization.yaml`).
2. **Subscription CRDs:** Parses OLM operator subscriptions (`kind: Subscription`) under cluster overlays and shared `components/operators/`.
3. **Canonical Normalization:** Maps raw subscription names to standard component keys:
   - `kubevirt-hyperconverged-operator` $\rightarrow$ `ocv`
   - `dell-csm-operator` $\rightarrow$ `dell-csm`
   - `portworx-operator` $\rightarrow$ `portworx`
   - `mtv-operator` / `forklift-operator` $\rightarrow$ `mtv`
4. **PostgreSQL Batch Upsert:** Stores clusters in `clusters` and all operator versions/channels in `component_versions`.

### 2. Secondary Live Fallback: Cluster API (`collectors/cluster_state.py`)
If live cluster connectivity is available, the agent connects using ServiceAccount user credentials dynamically retrieved from HashiCorp Vault (`VAULT_CLUSTER_CREDS_TEMPLATE=secret/data/clusters/{cluster}`) or `KUBECONFIG` and directly inspects:
- Active `ClusterVersion` object.
- Installed `ClusterServiceVersion` (CSVs) in `status.phase == 'Succeeded'`.

---

## Where and How the LLM Advisor is Used

The LLM layer (`engine/llm_advisor.py`) provides **strategic, multi-dimensional reasoning** on top of the deterministic rule engine.

### Key Use Cases:
1. **Major Version Architectural Drift (e.g. OCP 4 $\rightarrow$ 5):** Evaluates platform drift, deprecated API removals, and kernel re-certification requirements.
2. **Active Migration Motive Analysis:** Protects ongoing VMware-to-OCV migrations (`mtv` / `forklift`) from disruption during platform upgrades.
3. **CSI Storage Failover Gates:** Analyzes driver compatibility for Dell CSM (PowerStore/PowerFlex) and Portworx shared RWX volumes.
4. **TestOps Confluence Policy Synthesis:** Translates corporate qualification policies (`TESTOPS-POL-4082`) into actionable step-by-step qualification plans.

### Architectural Guardrails:
* **Additive Only:** The LLM can escalate a verdict (e.g., moving `GO` $\rightarrow$ `NO-GO (ESCALATE)` or adding caveats), but it **CANNOT overturn a deterministic blocker**.
* **Zero Hard Dependencies:** If no LLM endpoint is reachable, the built-in deterministic expert rule engine executes seamlessly with identical output schemas.
* **Production Gate:** Confluence TestOps governance is strictly enforced for all Production clusters.

---


---

## Running Pre-Upgrade Assessments

Use `run_assessment.py` to evaluate target OpenShift versions for single clusters or across an entire **50+ cluster fleet**:

### 1. Fleet-Wide 50+ Cluster Assessment
Evaluates all clusters in the PostgreSQL database against target OCP version, operator bounds, and Cincinnati graph:
```bash
python run_assessment.py --all --target 4.22.8
```

#### Fleet Output Matrix:
```text
==============================================================================
FLEET UPGRADE READINESS MATRIX: TARGET OCP 4.22.8
Total Clusters: 52 | Ready (GO): 38 | Caveats: 10 | Blocked (NO-GO): 4
==============================================================================
CLUSTER                  | CURRENT    | VERDICT          | BLOCKERS / CAVEATS
------------------------------------------------------------------------------
east-prod-01             | 4.22.2     | GO               | Clean
west-prod-02             | 4.21.14    | GO-WITH-CAVEATS  | 1 caveat(s)
south-edge-03            | 4.20.0     | NO-GO            | 3 blocker(s)
...
==============================================================================
```

### 2. Single Cluster Assessment with Dynamic Vault Login
Fetch cluster credentials dynamically from HashiCorp Vault for live pre-upgrade verification:
```bash
python run_assessment.py --cluster east-prod-01 --target 4.22.8 \
  --vault-kubeconfig-path secret/data/clusters/{cluster}
```

#### Sample Output:
```text
======================================================================
UPGRADE ASSESSMENT RESULT: GO
======================================================================

--- [RAW AUDIT JSON PAYLOAD] ---
{
  "cluster": "east-prod-01",
  "current_version": "4.22.2",
  "target_version": "4.22.8",
  "deterministic_verdict": "GO",
  "reasons": {
    "verdict": "go",
    "current_version": "4.22.2",
    "target_version": "4.22.8",
    "blockers": [],
    "caveats": [],
    "info": [
      "Upgrade path from 4.22.2 to 4.22.8 exists in Cincinnati graph.",
      "Operator 'mtv' version 2.8.0 verified compatible with 4.22.8.",
      "Operator 'dell-csm' version 1.11.0 verified compatible with 4.22.8.",
      "Operator 'portworx' version 25.3.0 verified compatible with 4.22.8."
    ]
  },
  "evaluated_at": "2026-08-16T22:18:39.512784+05:30"
}
```

---

### 2. Strategic Assessment with LLM Advisor
Combines the deterministic checks with **TestOps migration policy**, **major version drift analysis (e.g. OCP 4 $\rightarrow$ 5)**, **CSI storage failover gates**, and a **human sign-off checklist** (supports your local LLM server or built-in reasoning engine):
```bash
python run_assessment.py --cluster east-prod-01 --target 5.0.0 --llm
```

*(Optional: Point to custom local LLM endpoint or Confluence REST API placeholder)*:
```bash
python run_assessment.py --cluster east-prod-01 --target 5.0.0 --llm --llm-url http://127.0.0.1:8080/v1/chat/completions
```

#### Sample Output:
```text
======================================================================
UPGRADE ASSESSMENT RESULT: NO-GO (ESCALATE)
======================================================================

--- [EXECUTIVE SYNOPSIS] ---
RECOMMENDATION: HOLD UPGRADE (NO-GO ESCALATED). Upgrading cluster 'east-prod-01' from OCP 4.22.2 to 5.0.0 poses high operational risk to active migration and storage workloads. Identified 5 primary blocker(s) including version drift and operator boundary mismatches. Platform SRE and TestOps sign-off is strictly required prior to staging validation.

--- [ESCALATION & BLOCKER TRIGGERS] ---
 • Major version architectural drift detected (4.22.2 -> 5.0.0). Under TestOps Policy TESTOPS-POL-4082, major version transitions require mandatory sandbox qualification.
 • mtv (version 2.8.0) is NOT certified for OCP 5.0.0 (supported up to 4.22).
 • dell-csm (version 1.11.0) is NOT certified for OCP 5.0.0 (supported up to 4.22).
 • portworx (version 25.3.0) is NOT certified for OCP 5.0.0 (supported up to 4.22).
 • Active MTV (Migration Toolkit for Virtualization) operator v2.8.0 detected. VM migration stability is prioritized over routine platform upgrades unless critical CVEs are unpatched.

--- [DEEP COMPONENT & STORAGE IMPACT] ---
 • MIGRATION_IMPACT (MTV): HIGH RISK: Major/unsupported OCP version jump may break virt-v2v controller status streams, warm migration changed block tracking (CBT), and vSphere VDDK disk transfer pipes.
 • STORAGE_IMPACT (DELL CSM & PORTWORX): CRITICAL RISK: Storage CSI drivers (dell-csm, portworx) require kernel header validation and CSI node-driver re-certification on target Kubernetes base.
 • SECURITY_DELTA: 30 Critical and 832 Important CVE/RHSAs tracked in database. Target 5.0.0 incorporates recent security patches.

--- [TESTOPS REMEDIATION & QUALIFICATION PLAN] ---
 Step 1 [Pre-Requisite Operator Upgrades]:
   Action: Upgrade MTV to certified operator version (e.g. 2.8.0+) and Dell CSM / Portworx to latest supported z-stream in Pre-Prod.
   Gate:   Operator CSVs in Succeeded phase with 0 CrashLoopBackOff pods.
 Step 2 [Staging Sandbox Live Migration Test]:
   Action: Execute end-to-end VM warm migration dry run from VMware vSphere to OCV on target OCP build.
   Gate:   Zero data corruption, successful cutover under 60 seconds.
 Step 3 [CSI Storage Failover Verification]:
   Action: Trigger node drain and worker reboot while running I/O load on Dell CSM (PowerStore/PowerFlex) and Portworx RWX volumes.
   Gate:   Volumes reattach within 30s without VolumeAttachment timeout.
 Step 4 [Fleet Canary Deployment]:
   Action: Roll out upgrade to 1 non-prod lab cluster before scheduling production fleet windows.
   Gate:   ClusterVersion reaches Available=True with 0 cluster operator degraded alerts for 48 hours.

--- [HUMAN-IN-THE-LOOP SIGN-OFF GATE] ---
 Status: PENDING_APPROVAL
 Required Approvers: TestOps Lead, Cloud Platform SRE Lead, Storage Administrator
 Checklist:
   [ ] All active MTV VM migrations paused / drained
   [ ] Dell CSM / Portworx sandbox failover test passed
   [ ] TestOps qualification test suite executed on target build
   [ ] Maintenance window approved by Change Advisory Board (CAB)
```

---

## Automating GitOps Upgrade Pull Requests

Once an upgrade assessment is persisted in the database, `run_gitops_pr.py` can automatically open or update a GitOps PR bumping the target OCP version across your fleet (e.g. Advanced Cluster Management / OpenShift GitOps `ClusterCurator` manifests):

### Key Safety Gates & Features:
1. **Assessment-Gated Execution:** Refuses outright on a `NO-GO` verdict, printing blocking reasons and exiting nonzero without touching Git or GitHub APIs.
2. **Draft by Default for Caveats:** Opens PRs as **Draft** if the verdict is `GO-WITH-CAVEATS` (override with `--force-ready` to open ready-for-review).
3. **Round-Trip YAML Preservation:** Uses `ruamel.yaml` to modify ACM `ClusterCurator` CRs (`spec.desiredCuration: upgrade`, `spec.upgrade.desiredUpdate`), preserving existing comments, indentation, and structure.
4. **Idempotent Updates:** Re-running against an existing upgrade branch updates the PR in place rather than creating duplicates.
5. **Dry-Run Mode:** Generate commit diffs and full Markdown PR bodies without requiring `$GITHUB_TOKEN` or pushing to remote.

### Usage Examples:

```bash
# 1. Preview GitOps PR changes and generated Markdown body (no token required):
python run_gitops_pr.py --cluster east-prod-01 --target 4.22.8 --dry-run

# 2. Open / update PR on GitHub:
export GITHUB_TOKEN=ghp_yourPersonalAccessToken
python run_gitops_pr.py --cluster east-prod-01 --target 4.22.8

# 3. Force open ready-for-review on GO-WITH-CAVEATS:
python run_gitops_pr.py --cluster east-prod-01 --target 4.22.8 --force-ready
```

### GitOps Fleet Configuration:
Cluster repositories and paths are configured in [`data/gitops_targets.yaml`](file:///c:/Users/SRIMANDARBHA/Projects/ocv-upgrade-agent/ocv-upgrade-agent/data/gitops_targets.yaml):
```yaml
defaults:
  repo_url: "https://github.com/example-org/ocp-gitops-fleet.git"
  owner: "example-org"
  repo_name: "ocp-gitops-fleet"
  base_branch: "main"
  curator_namespace: "clusters"

clusters:
  east-prod-01:
    cluster_path: "clusters/east-prod-01"
    curator_namespace: "east-prod-01"
    upstream_graph_url: "http://cincinnati.internal.net/api/upgrades_info/v1/graph"
```

---

## Bastion vs. Disconnected Split

| Component | Network Requirement | Execution Location |
| :--- | :--- | :--- |
| `redhat_security` | Internet egress (`access.redhat.com`) | Connected Bastion |
| `lifecycle` | Internet egress (`access.redhat.com`) | Connected Bastion |
| `cincinnati` | Public API *or* local OSUS instance | Bastion (public) or Disconnected (OSUS route) |
| `vendor_matrix` | None (reads checked-in YAML) | Either |
| `cluster_state` | Kubernetes API access | Disconnected cluster network |
| `release_info` | `oc` binary + mirrored registry | Disconnected cluster network |
| `run_assessment` | PostgreSQL access | Disconnected / Central Management Hub |

---

## Operator Compatibility Support (MTV, Dell CSM, Portworx)

Compatibility rules are declared in [`data/vendor_matrix_seed.yaml`](file:///c:/Users/SRIMANDARBHA/Projects/ocv-upgrade-agent/ocv-upgrade-agent/data/vendor_matrix_seed.yaml):

* **MTV (Migration Toolkit for Virtualization):** Tracks certified OCP bounds (`min_ocp`, `max_ocp`) for v2.6, v2.7, v2.8+, warm migration changed block tracking (CBT) requirements, and VMware VDDK integration.
* **Dell CSM:** Tracks PowerStore, PowerFlex, PowerScale, and PowerMax CSI driver support across OCP 4.18 through 4.22.
* **Portworx Enterprise:** Tracks sharedv4 RWX block storage support and live VM migration requirements.

---

## Confluence REST API Integration (Placeholder)

The agent contains a modular Confluence loader placeholder (`fetch_confluence_policy` in [`engine/llm_advisor.py`](file:///c:/Users/SRIMANDARBHA/Projects/ocv-upgrade-agent/ocv-upgrade-agent/engine/llm_advisor.py)) to dynamically ingest TestOps qualification policies directly from Atlassian Confluence Cloud or Data Center REST APIs:

* **Endpoint:** `GET {CONFLUENCE_URL}/wiki/rest/api/content/{PAGE_ID}?expand=body.storage`
* **Configuration:**
  ```env
  CONFLUENCE_URL=https://your-domain.atlassian.net
  CONFLUENCE_PAGE_ID=123456789
  CONFLUENCE_API_TOKEN=your_token
  ```
* **Fallback Behavior:** If Confluence API parameters are omitted, the agent seamlessly uses the verified local policy standards in [`data/testops_confluence_policy.md`](file:///c:/Users/SRIMANDARBHA/Projects/ocv-upgrade-agent/ocv-upgrade-agent/data/testops_confluence_policy.md).

---

## Running Tests

Unit tests execute entirely against saved mock fixtures without requiring live network calls:

```bash
pytest
```
