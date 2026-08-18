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
collectors/
  redhat_security.py           CVE + CSAF/errata -> advisories
  lifecycle.py                 GA/EOL dates      -> product_lifecycle
  cincinnati.py                OSUS upgrade graph-> upgrade_edges
  vendor_matrix.py             Dell/Portworx/MTV -> operator_compat
  cluster_state.py             Live cluster state-> component_versions
  release_info.py              Release images    -> release_images
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
run_collectors.py              Orchestrator for all data collectors
run_assessment.py              CLI entrypoint for running cluster compatibility assessments
run_gitops_pr.py               CLI entrypoint for opening/updating GitOps upgrade PRs
tests/                         Unit tests against saved fixtures (no live network needed)
```

---

## Setup & Database Configuration

### 1. Install Dependencies
```bash
python -m venv venv
# On Linux/macOS:
source venv/bin/activate
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### 2. Configure `.env`
Create a `.env` file in the root directory (or copy from `.env.example`):
```env
# PostgreSQL connection URL
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/ocv_agent

# Cincinnati/OSUS upgrade graph base URL
# Bastion (public):   https://api.openshift.com
# Disconnected (OSUS): http://<local-osus-route>
CINCINNATI_URL=https://api.openshift.com

# Kubeconfig context for live cluster inspection
KUBECONFIG=/etc/ocv-agent/kubeconfig
```

### 3. Initialize Database Tables
Tables are created automatically on the first run, or you can apply the DDL directly:
```bash
psql -U postgres -h localhost -d ocv_agent -f db/schema.sql
```

---

## Running Data Collectors

The `run_collectors.py` orchestrator populates your database. You can run all collectors or select specific feeds:

### Examples

```bash
# 1. Run all online collectors from connected Bastion:
python run_collectors.py --only redhat-security,lifecycle,cincinnati

# 2. Pull Cincinnati graph for a specific channel (e.g., stable-4.22):
python run_collectors.py --only cincinnati --channel stable-4.22

# 3. Pull security advisories with severity or date filters:
python run_collectors.py --only redhat-security --severity critical --after 2026-01-01

# 4. Ingest MTV, Dell CSM, and Portworx compatibility seed matrices:
python run_collectors.py --only vendor-matrix

# 5. Inspect mirrored release payload in air-gapped network:
python run_collectors.py --only release-info --release-version 4.22.8
```

---

## Running Pre-Upgrade Assessments

Use `run_assessment.py` to evaluate whether a target OpenShift version is safe for a cluster.

### 1. Deterministic Assessment (GO / NO-GO)
Evaluates Cincinnati graph connectivity, conditional update risks, operator bounds, and EOL dates:
```bash
python run_assessment.py --cluster east-prod-01 --target 4.22.8
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
