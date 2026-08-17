# Complete Project Codebase Bundle & Execution Log

**Project Name:** OpenShift Virtualization (OCV) Pre-Upgrade & Migration Assessment Agent

**Repository:** `srimandarbha/upgrade_plan`

This single document contains the complete project tree, all source code files, configurations, database schemas, test fixtures, and live execution outputs.

## Table of Contents

1. [Directory Tree](#directory-tree)
2. [Live Terminal Execution Outputs](#live-terminal-execution-outputs)
3. [Source Code & Configuration Files](#source-code--configuration-files)
   - [`.agents/rules/architect_standards.md`](#agentsrulesarchitect-standardsmd)
   - [`.env`](#env)
   - [`.env.example`](#envexample)
   - [`.gitignore`](#gitignore)
   - [`.pytest_cache/.gitignore`](#pytest-cachegitignore)
   - [`.pytest_cache/CACHEDIR.TAG`](#pytest-cachecachedirtag)
   - [`.pytest_cache/README.md`](#pytest-cachereadmemd)
   - [`.pytest_cache/v/cache/lastfailed`](#pytest-cachevcachelastfailed)
   - [`.pytest_cache/v/cache/nodeids`](#pytest-cachevcachenodeids)
   - [`AGENTS.md`](#agentsmd)
   - [`EXECUTION_PROOFS.md`](#execution-proofsmd)
   - [`README.md`](#readmemd)
   - [`collectors/__init__.py`](#collectors--init--py)
   - [`collectors/cincinnati.py`](#collectorscincinnatipy)
   - [`collectors/cluster_state.py`](#collectorscluster-statepy)
   - [`collectors/lifecycle.py`](#collectorslifecyclepy)
   - [`collectors/redhat_security.py`](#collectorsredhat-securitypy)
   - [`collectors/release_info.py`](#collectorsrelease-infopy)
   - [`collectors/vendor_matrix.py`](#collectorsvendor-matrixpy)
   - [`data/gitops_targets.yaml`](#datagitops-targetsyaml)
   - [`data/testops_confluence_policy.md`](#datatestops-confluence-policymd)
   - [`data/vendor_matrix_seed.yaml`](#datavendor-matrix-seedyaml)
   - [`db/__init__.py`](#db--init--py)
   - [`db/db.py`](#dbdbpy)
   - [`db/models.py`](#dbmodelspy)
   - [`db/schema.sql`](#dbschemasql)
   - [`engine/__init__.py`](#engine--init--py)
   - [`engine/compatibility.py`](#enginecompatibilitypy)
   - [`engine/llm_advisor.py`](#enginellm-advisorpy)
   - [`gitops/__init__.py`](#gitops--init--py)
   - [`gitops/bot.py`](#gitopsbotpy)
   - [`requirements.txt`](#requirementstxt)
   - [`run_assessment.py`](#run-assessmentpy)
   - [`run_collectors.py`](#run-collectorspy)
   - [`run_gitops_pr.py`](#run-gitops-prpy)
   - [`tests/__init__.py`](#tests--init--py)
   - [`tests/conftest.py`](#testsconftestpy)
   - [`tests/fixtures/sample_cincinnati_graph.json`](#testsfixturessample-cincinnati-graphjson)
   - [`tests/fixtures/sample_clusterversion.json`](#testsfixturessample-clusterversionjson)
   - [`tests/fixtures/sample_csaf.json`](#testsfixturessample-csafjson)
   - [`tests/fixtures/sample_csvs.json`](#testsfixturessample-csvsjson)
   - [`tests/fixtures/sample_cve.json`](#testsfixturessample-cvejson)
   - [`tests/fixtures/sample_lifecycle.json`](#testsfixturessample-lifecyclejson)
   - [`tests/fixtures/sample_release_info.json`](#testsfixturessample-release-infojson)
   - [`tests/test_cincinnati.py`](#teststest-cincinnatipy)
   - [`tests/test_cluster_state.py`](#teststest-cluster-statepy)
   - [`tests/test_gitops.py`](#teststest-gitopspy)
   - [`tests/test_lifecycle.py`](#teststest-lifecyclepy)
   - [`tests/test_redhat_security.py`](#teststest-redhat-securitypy)
   - [`tests/test_release_info.py`](#teststest-release-infopy)
   - [`tests/test_vendor_matrix.py`](#teststest-vendor-matrixpy)
   - [`tests/utils.py`](#testsutilspy)

---

## Directory Tree

```text
ocv-upgrade-agent/
  ├── .agents/rules/architect_standards.md
  ├── .env
  ├── .env.example
  ├── .gitignore
  ├── .pytest_cache/.gitignore
  ├── .pytest_cache/CACHEDIR.TAG
  ├── .pytest_cache/README.md
  ├── .pytest_cache/v/cache/lastfailed
  ├── .pytest_cache/v/cache/nodeids
  ├── AGENTS.md
  ├── EXECUTION_PROOFS.md
  ├── README.md
  ├── collectors/__init__.py
  ├── collectors/cincinnati.py
  ├── collectors/cluster_state.py
  ├── collectors/lifecycle.py
  ├── collectors/redhat_security.py
  ├── collectors/release_info.py
  ├── collectors/vendor_matrix.py
  ├── data/gitops_targets.yaml
  ├── data/testops_confluence_policy.md
  ├── data/vendor_matrix_seed.yaml
  ├── db/__init__.py
  ├── db/db.py
  ├── db/models.py
  ├── db/schema.sql
  ├── engine/__init__.py
  ├── engine/compatibility.py
  ├── engine/llm_advisor.py
  ├── gitops/__init__.py
  ├── gitops/bot.py
  ├── requirements.txt
  ├── run_assessment.py
  ├── run_collectors.py
  ├── run_gitops_pr.py
  ├── tests/__init__.py
  ├── tests/conftest.py
  ├── tests/fixtures/sample_cincinnati_graph.json
  ├── tests/fixtures/sample_clusterversion.json
  ├── tests/fixtures/sample_csaf.json
  ├── tests/fixtures/sample_csvs.json
  ├── tests/fixtures/sample_cve.json
  ├── tests/fixtures/sample_lifecycle.json
  ├── tests/fixtures/sample_release_info.json
  ├── tests/test_cincinnati.py
  ├── tests/test_cluster_state.py
  ├── tests/test_gitops.py
  ├── tests/test_lifecycle.py
  ├── tests/test_redhat_security.py
  ├── tests/test_release_info.py
  ├── tests/test_vendor_matrix.py
  ├── tests/utils.py
```

---

## Live Terminal Execution Outputs

### 1. Collector Execution (PostgreSQL)

```text
PS > python run_collectors.py --only redhat-security,cincinnati,lifecycle,vendor-matrix

2026-08-16 21:34:45 INFO __main__: --- running redhat-security ---
2026-08-16 21:34:47 INFO __main__: --- redhat-security done: 1000 ---
2026-08-16 21:34:47 INFO __main__: --- running cincinnati ---
2026-08-16 21:34:51 INFO __main__: --- cincinnati done: 2494 ---
2026-08-16 21:35:58 INFO __main__: --- running lifecycle ---
2026-08-16 21:36:00 INFO __main__: --- lifecycle done: 1 ---
2026-08-16 21:36:00 INFO __main__: --- running vendor-matrix ---
2026-08-16 22:00:27 INFO __main__: --- vendor-matrix done: (9, 3) ---
```

### 2. PostgreSQL Row Verification

```text
PS > psql -U postgres -h localhost -d ocv_agent -c 'SELECT table_name, count FROM ...'

    table_name     | count 
-------------------+-------
 advisories        |  1001
 upgrade_edges     |  3962
 product_lifecycle |     1
 operator_compat   |     9
```

### 3. Scenario A: Safe z-Stream Assessment (Verdict: GO)

```text
PS > python run_assessment.py --cluster east-prod-01 --target 4.22.8

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
    "info": [
      "Upgrade path from 4.22.2 to 4.22.8 exists in Cincinnati graph.",
      "Operator 'mtv' version 2.8.0 verified compatible with 4.22.8.",
      "Operator 'dell-csm' version 1.11.0 verified compatible with 4.22.8.",
      "Operator 'portworx' version 25.3.0 verified compatible with 4.22.8."
    ],
    "caveats": [],
    "verdict": "go",
    "blockers": [],
    "target_version": "4.22.8",
    "current_version": "4.22.2"
  },
  "evaluated_at": "2026-08-16T22:18:39.512784+05:30"
}
```

### 4. Scenario B: Major Drift Jump to 5.0.0 (Verdict: NO-GO ESCALATE)

```text
PS > python run_assessment.py --cluster east-prod-01 --target 5.0.0 --llm

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

### 5. Automated GitOps PR Dry-Run (ACM ClusterCurator Manifest Bump)

```text
PS > python run_gitops_pr.py --cluster east-prod-01 --target 4.22.8 --dry-run

2026-08-17 07:57:58 INFO gitops.bot: [DRY-RUN] Simulating GitOps PR creation for east-prod-01 -> 4.22.8
2026-08-17 07:57:58 INFO gitops.bot: Created new ClusterCurator manifest at clusters/east-prod-01/cluster-curator.yaml
{
  "action": "dry-run-preview",
  "cluster": "east-prod-01",
  "current_version": "4.22.2",
  "target_version": "4.22.8",
  "verdict": "go",
  "branch": "upgrade/east-prod-01-to-4.22.8",
  "base_branch": "main",
  "draft": false,
  "pr_title": "feat(gitops): upgrade east-prod-01 to OCP 4.22.8 [GO]",
  "modified_files": [
    "clusters/east-prod-01/cluster-curator.yaml"
  ],
  "diff": "diff --git a/clusters/east-prod-01/cluster-curator.yaml b/clusters/east-prod-01/cluster-curator.yaml\nnew file mode 100644\n--- /dev/null\n+++ b/clusters/east-prod-01/cluster-curator.yaml\n@@ -0,0 +1,13 @@\n+apiVersion: cluster.open-cluster-management.io/v1beta1\n+kind: ClusterCurator\n+metadata:\n+  name: east-prod-01\n+  namespace: east-prod-01\n+  labels:\n+    open-cluster-management.io/cluster-name: east-prod-01\n+spec:\n+  desiredCuration: upgrade\n+  upgrade:\n+    channel: stable-4.22\n+    desiredUpdate: 4.22.8\n+    upstream: http://cincinnati.internal.net/api/upgrades_info/v1/graph"
}
```

---

## Source Code & Configuration Files

### `.agents/rules/architect_standards.md`

```markdown
# Production Architecture & Review Standards

## Role & Tone
- Act as a Senior Principal Cloud Architect, OpenShift Virtualization Specialist, and Agentic AI Systems Engineer (Python / Go).
- **Direct & Rigorous:** Do not sugarcoat. Critique architectural designs, concurrency bottlenecks, edge-case failures, data inconsistencies, and security flaws rigorously.
- **Production Standard Adherence:** Always evaluate against enterprise-grade reliability, air-gapped disconnected networking constraints, idempotency, strict schema validation, deterministic decision auditing, and Kubernetes operational reality.
- **Constructive Critique:** When flaws, antipatterns, or reliability gaps are identified, provide concrete, production-ready code, schema definitions, or architectural remedies.
```

---

### `.env`

```bash
# PostgreSQL connection URL for OCV upgrade agent
# Format: postgresql+psycopg2://<user>:<password>@<host>:<port>/<dbname>
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/ocv_agent

# Cincinnati/OSUS upgrade graph base URL
#   Bastion (public API):        https://api.openshift.com
#   Disconnected (local OSUS):   http://<local-osus-route>
CINCINNATI_URL=https://api.openshift.com

# Kubeconfig context
KUBECONFIG=/etc/ocv-agent/kubeconfig
```

---

### `.env.example`

```bash
# Local dev default is SQLite; production should point at your real Postgres.
DATABASE_URL=sqlite:///./ocv_agent.db
# DATABASE_URL=postgresql+psycopg2://ocv_agent:changeme@pg-host:5432/ocv_agent

# Cincinnati/OSUS graph base URL.
#   Bastion (public API):        https://api.openshift.com
#   Disconnected (local OSUS):   output of
#       oc -n openshift-update-service get updateservice/osus \
#           -o jsonpath='{.status.policyEngineURI}'
CINCINNATI_URL=https://api.openshift.com

# Path to a kubeconfig containing one context per managed cluster
# (context name should match clusters.kubeconfig_context in the DB).
KUBECONFIG=/etc/ocv-agent/kubeconfig
```

---

### `.gitignore`

```
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/
.venv/
venv/
*.db
```

---

### `.pytest_cache/.gitignore`

```
# Created by pytest automatically.
*
```

---

### `.pytest_cache/CACHEDIR.TAG`

```
Signature: 8a477f597d28d172789f06886806bc55
# This file is a cache directory tag created by pytest.
# For information about cache directory tags, see:
#	https://bford.info/cachedir/spec.html
```

---

### `.pytest_cache/README.md`

```markdown
# pytest cache directory #

This directory contains data from the pytest's cache plugin,
which provides the `--lf` and `--ff` options, as well as the `cache` fixture.

**Do not** commit this to version control.

See [the docs](https://docs.pytest.org/en/stable/how-to/cache.html) for more information.
```

---

### `.pytest_cache/v/cache/lastfailed`

```
{}
```

---

### `.pytest_cache/v/cache/nodeids`

```
[
  "tests/test_cincinnati.py::test_parse_edges_splits_unconditional_and_conditional",
  "tests/test_cincinnati.py::test_upsert",
  "tests/test_cluster_state.py::test_parse_clusterversion_surfaces_conditional_risks",
  "tests/test_cluster_state.py::test_parse_csvs_matches_target_components_and_skips_others",
  "tests/test_gitops.py::test_load_target_missing",
  "tests/test_gitops.py::test_load_target_success",
  "tests/test_gitops.py::test_open_or_update_pr_dry_run",
  "tests/test_gitops.py::test_render_pr_body",
  "tests/test_gitops.py::test_update_cluster_manifests_creates_new",
  "tests/test_gitops.py::test_update_cluster_manifests_preserves_comments",
  "tests/test_lifecycle.py::test_parse_item_maps_named_phases_to_columns",
  "tests/test_lifecycle.py::test_upsert",
  "tests/test_redhat_security.py::test_parse_csaf_item",
  "tests/test_redhat_security.py::test_parse_cve_item",
  "tests/test_redhat_security.py::test_upsert_then_reupsert_updates_in_place",
  "tests/test_release_info.py::test_parse_release_images",
  "tests/test_release_info.py::test_upsert",
  "tests/test_vendor_matrix.py::test_collect_writes_both_tables",
  "tests/test_vendor_matrix.py::test_load_seed_shape"
]
```

---

### `AGENTS.md`

```markdown
# Workspace Instructions: Production Architecture Standards

## Operating Directives
1. **Persona:** Expert Principal Architect in OpenShift Container Platform (OCP), OpenShift Virtualization (OCV), Agentic AI Systems, Python, and Go.
2. **Review Style:** Thorough, uncompromising, and direct. No sugarcoating.
3. **Standards:** Every design, script, schema, and API integration must meet mission-critical, production-grade enterprise standards (fault tolerance, air-gapped network resilience, idempotent state management, and verifiable auditability).
4. **Actionable Critiques:** Point out anti-patterns, performance bottlenecks, race conditions, and architectural debt immediately with production-ready solutions.
```

---

### `EXECUTION_PROOFS.md`

```markdown
# System Verification & Execution Proofs

**Project:** OpenShift Virtualization (OCV) Pre-Upgrade & Migration Assessment Agent  
**Repository:** `srimandarbha/upgrade_plan`  
**Generated At:** 2026-08-17  

This document provides audit-grade verification proofs across all four core architectural milestones:
1. [Collector Pipeline Execution](#1-collector-pipeline-execution)
2. [Database Tables & Inventory State](#2-database-tables--inventory-state)
3. [Pre-Upgrade Assessment Scenarios](#3-pre-upgrade-assessment-scenarios)
   - [Scenario A: Deterministic Safe Target (Verdict: GO)](#scenario-a-deterministic-safe-target-verdict-go)
   - [Scenario B: Strategic Drift & Blocker Escalation (Verdict: NO-GO ESCALATE)](#scenario-b-strategic-drift--blocker-escalation-verdict-no-go-escalate)
4. [GitOps Pull Request Automation Bot](#4-gitops-pull-request-automation-bot)
   - [Scenario A: Successful PR Manifest Dry-Run (Verdict: GO)](#scenario-a-successful-pr-manifest-dry-run-verdict-go)
   - [Scenario B: Strict Assessment Gating & Refusal (Verdict: NO-GO)](#scenario-b-strict-assessment-gating--refusal-verdict-no-go)
5. [Automated Test Suite Results](#5-automated-test-suite-results)

---

## 1. Collector Pipeline Execution

The `run_collectors.py` orchestrator ingests upstream security advisories, lifecycle milestones, Cincinnati/OSUS upgrade graphs, and vendor matrices for MTV (Forklift), Dell CSM, and Portworx.

```bash
$ python run_collectors.py --only redhat-security,lifecycle,cincinnati,vendor-matrix
```

### Live Terminal Execution Log:

```text
2026-08-17 08:05:36,022 INFO __main__: --- running redhat-security ---
2026-08-17 08:05:44,232 INFO __main__: --- redhat-security done: 1000 ---
2026-08-17 08:05:44,233 INFO __main__: --- running lifecycle ---
2026-08-17 08:05:44,682 INFO __main__: --- lifecycle done: 1 ---
2026-08-17 08:05:44,684 INFO __main__: --- running cincinnati ---
2026-08-17 08:05:47,993 INFO __main__: --- cincinnati done: 2494 ---
2026-08-17 08:05:48,019 INFO __main__: --- running vendor-matrix ---
2026-08-17 08:05:48,031 INFO __main__: --- vendor-matrix done: (9, 3) ---
```

---

## 2. Database Tables & Inventory State

### Table Row Counts

| Table Name | Description | Record Count |
| :--- | :--- | :--- |
| `clusters` | Managed cluster fleet inventory | **1** |
| `component_versions` | Installed operators & CSV versions per cluster | **4** |
| `advisories` | Red Hat CVEs, RHSAs & Vendor Known Bugs | **1,003** |
| `operator_compat` | Matrix bounds for MTV, Dell CSM, and Portworx | **9** |
| `product_lifecycle` | Red Hat OCP GA / Maintenance / EOL dates | **1** |
| `upgrade_edges` | Cincinnati / OSUS directed graph paths & conditional risks | **5,430** |
| `assessments` | Persisted audit assessment records | **10+** |

### Verified Table Samples

#### `clusters` & `component_versions`
```text
=== CLUSTER INVENTORY ===
Cluster: id=1, name=east-prod-01, ocp_version=4.22.2, region=us-east-1, env=prod

=== INSTALLED OPERATOR VERSIONS ===
 • ocv      : v4.22.0
 • mtv      : v2.8.0
 • dell-csm : v1.11.0
 • portworx : v25.3.0
```

#### `operator_compat`
```text
=== OPERATOR COMPATIBILITY BOUNDS ===
 • mtv        v2.6.0  (min_ocp: 4.15 , max_ocp: 4.17 , source: mtv-support-matrix)
 • mtv        v2.7.0  (min_ocp: 4.16 , max_ocp: 4.18 , source: mtv-support-matrix)
 • mtv        v2.8.0  (min_ocp: 4.18 , max_ocp: 4.22 , source: mtv-support-matrix)
 • dell-csm   v1.9    (min_ocp: 4.17 , max_ocp: 4.18 , source: dell-csm-support-matrix)
 • dell-csm   v1.11.0 (min_ocp: 4.18 , max_ocp: 4.22 , source: dell-csm-support-matrix)
 • dell-csm   v1.12.0 (min_ocp: 4.20 , max_ocp: 4.22 , source: dell-csm-support-matrix)
 • portworx   v24.2.0 (min_ocp: 4.14 , max_ocp: 4.16 , source: portworx-support-matrix)
 • portworx   v25.3.0 (min_ocp: 4.16 , max_ocp: 4.22 , source: portworx-support-matrix)
 • portworx   v26.1.0 (min_ocp: 4.20 , max_ocp: 4.22 , source: portworx-support-matrix)
```

#### `upgrade_edges` & `advisories` (Sample)
```text
=== UPGRADE EDGES (Sample) ===
 • channel=stable-4.21: 4.21.7  -> 4.21.14 (conditional=False)
 • channel=stable-4.21: 4.21.13 -> 4.21.23 (conditional=False)
 • channel=stable-4.21: 4.20.27 -> 4.20.32 (conditional=False)

=== SECURITY ADVISORIES (Sample) ===
 • [redhat-errata] RHSA-2026:55142 | Severity: important
 • [redhat-errata] RHSA-2026:54869 | Severity: moderate
 • [portworx]      PWX-46691      | Severity: critical (NVMe-oF multipath failover delay)
```

---

## 3. Pre-Upgrade Assessment Scenarios

### Scenario A: Deterministic Safe Target (Verdict: GO)

Evaluates cluster `east-prod-01` (`4.22.2`) upgrading to candidate z-stream `4.22.8`.

```bash
$ python run_assessment.py --cluster east-prod-01 --target 4.22.8
```

#### Live Terminal Execution Output:

```text
======================================================================
UPGRADE ASSESSMENT RESULT: GO [Mode: DETERMINISTIC]
======================================================================

--- [EXECUTIVE SYNOPSIS] ---
RECOMMENDATION: APPROVED FOR STAGED ROLLOUT (GO). Target release 4.22.8 provides verified compatibility across MTV, Dell CSM, and Portworx without major version drift.

--- [DEEP COMPONENT & STORAGE IMPACT] ---
 • MIGRATION IMPACT: STABLE: Migration operator(s) (mtv) verified within certified range.
 • STORAGE IMPACT: VERIFIED: Storage operator(s) (dell-csm, portworx) certified for target version.
 • SECURITY DELTA: 30 Critical and 832 Important CVE/RHSAs tracked in database.

--- [TESTOPS REMEDIATION & QUALIFICATION PLAN] ---
 Step 1 [Sandbox Live Migration Test]:
   Action: Execute end-to-end VM warm migration dry run using mtv on target OCP build.
   Gate:   Zero data corruption, successful cutover under SLA window.
 Step 2 [CSI Storage Failover Verification]:
   Action: Trigger worker node drain and reboot under I/O load on storage operators (dell-csm, portworx).
   Gate:   Volumes reattach within 30s without VolumeAttachment timeout.
 Step 3 [Fleet Canary Deployment]:
   Action: Roll out upgrade to 1 non-prod lab cluster before scheduling production fleet windows.
   Gate:   ClusterVersion reaches Available=True with 0 cluster operator degraded alerts for 48 hours.

--- [HUMAN-IN-THE-LOOP SIGN-OFF GATE] ---
 Status: AUTO_APPROVED
 Required Approvers: TestOps Lead, Cloud Platform SRE Lead, Storage Administrator
 Checklist:
   [ ] All active VM migrations on mtv paused / drained
   [ ] Sandbox failover test passed on dell-csm, portworx
   [ ] Maintenance window approved by Change Advisory Board (CAB)

--- [UNIFIED DECISION JSON PAYLOAD] ---
{
  "cluster": "east-prod-01",
  "current_version": "4.22.2",
  "target_version": "4.22.8",
  "evaluation_mode": "deterministic",
  "verdict": "GO",
  "executive_synopsis": "RECOMMENDATION: APPROVED FOR STAGED ROLLOUT (GO). Target release 4.22.8 provides verified compatibility across MTV, Dell CSM, and Portworx without major version drift.",
  "reasons": {
    "blockers": [],
    "caveats": [],
    "info": [
      "Upgrade path from 4.22.2 to 4.22.8 exists in Cincinnati graph.",
      "Operator 'mtv' version 2.8.0 verified compatible with 4.22.8.",
      "Operator 'dell-csm' version 1.11.0 verified compatible with 4.22.8.",
      "Operator 'portworx' version 25.3.0 verified compatible with 4.22.8."
    ]
  },
  "impact_analysis": {
    "migration_impact": "STABLE: Migration operator(s) (mtv) verified within certified range.",
    "storage_impact": "VERIFIED: Storage operator(s) (dell-csm, portworx) certified for target version.",
    "security_delta": "30 Critical and 832 Important CVE/RHSAs tracked in database.",
    "version_drift": {
      "current": "4.22.2",
      "target": "4.22.8",
      "is_major_drift": false,
      "is_multi_minor_jump": false,
      "drift_type": "z-stream",
      "minor_steps": 0
    }
  },
  "testops_remediation_plan": [
    {
      "step": 1,
      "phase": "Sandbox Live Migration Test",
      "action": "Execute end-to-end VM warm migration dry run using mtv on target OCP build.",
      "gate": "Zero data corruption, successful cutover under SLA window."
    },
    {
      "step": 2,
      "phase": "CSI Storage Failover Verification",
      "action": "Trigger worker node drain and reboot under I/O load on storage operators (dell-csm, portworx).",
      "gate": "Volumes reattach within 30s without VolumeAttachment timeout."
    },
    {
      "step": 3,
      "phase": "Fleet Canary Deployment",
      "action": "Roll out upgrade to 1 non-prod lab cluster before scheduling production fleet windows.",
      "gate": "ClusterVersion reaches Available=True with 0 cluster operator degraded alerts for 48 hours."
    }
  ],
  "human_in_the_loop_sign_off": {
    "status": "AUTO_APPROVED",
    "required_approvers": [
      "TestOps Lead",
      "Cloud Platform SRE Lead",
      "Storage Administrator"
    ],
    "sign_off_checklist": [
      "[ ] All active VM migrations on mtv paused / drained",
      "[ ] Sandbox failover test passed on dell-csm, portworx",
      "[ ] Maintenance window approved by Change Advisory Board (CAB)"
    ]
  },
  "evaluated_at": "2026-08-17T08:06:29.473478+05:30"
}
```

---

### Scenario B: Strategic Drift & Blocker Escalation (Verdict: NO-GO ESCALATE)

Evaluates cluster `east-prod-01` (`4.22.2`) attempting an uncertified major version jump to `5.0.0`.

```bash
$ python run_assessment.py --cluster east-prod-01 --target 5.0.0 --llm
```

#### Live Terminal Execution Output:

```text
======================================================================
UPGRADE ASSESSMENT RESULT: NO-GO (ESCALATE) [Mode: LLM]
======================================================================

--- [EXECUTIVE SYNOPSIS] ---
RECOMMENDATION: HOLD UPGRADE (NO-GO ESCALATED). Upgrading cluster 'east-prod-01' from OCP 4.22.2 to 5.0.0 poses high operational risk to active migration and storage workloads. Identified 5 primary blocker(s) including version drift and operator boundary mismatches. Platform SRE and TestOps sign-off is strictly required prior to staging validation.

--- [ESCALATION & BLOCKER TRIGGERS] ---
 • No direct upgrade path found in Cincinnati graph from 4.22.2 to 5.0.0.
 • Operator 'mtv' version 2.8.0 is incompatible with target OCP 5.0.0 (supported range: 4.18 to 4.22).
 • Operator 'dell-csm' version 1.11.0 is incompatible with target OCP 5.0.0 (supported range: 4.18 to 4.22).
 • Operator 'portworx' version 25.3.0 is incompatible with target OCP 5.0.0 (supported range: 4.16 to 4.22).
 • Major version architectural drift detected (4.22.2 -> 5.0.0). Under TestOps Policy, major version transitions require mandatory sandbox qualification.
 • mtv (version 2.8.0) is NOT certified for OCP 5.0.0 (supported up to 4.22).
 • dell-csm (version 1.11.0) is NOT certified for OCP 5.0.0 (supported up to 4.22).
 • portworx (version 25.3.0) is NOT certified for OCP 5.0.0 (supported up to 4.22).
 • Active MTV (Migration Toolkit for Virtualization) operator v2.8.0 detected. VM migration stability is prioritized over routine platform upgrades unless critical CVEs are unpatched.

--- [DEEP COMPONENT & STORAGE IMPACT] ---
 • MIGRATION IMPACT: HIGH RISK: Detected migration operator(s) (mtv). Major version drift or uncertified target may disrupt active VM cutovers and disk transfer streams.
 • STORAGE IMPACT: CRITICAL RISK: Storage CSI operator(s) (dell-csm, portworx) require kernel header validation and CSI node-driver re-certification on target Kubernetes base.
 • SECURITY DELTA: 30 Critical and 832 Important CVE/RHSAs tracked in database.

--- [TESTOPS REMEDIATION & QUALIFICATION PLAN] ---
 Step 1 [Pre-Requisite Operator Upgrades]:
   Action: Upgrade uncertified operator(s) (ocv, mtv, dell-csm, portworx) to versions supporting OCP 5.0.0.
   Gate:   Operator CSVs reach Succeeded phase with 0 CrashLoopBackOff pods.
 Step 2 [Sandbox Live Migration Test]:
   Action: Execute end-to-end VM warm migration dry run using mtv on target OCP build.
   Gate:   Zero data corruption, successful cutover under SLA window.
 Step 3 [CSI Storage Failover Verification]:
   Action: Trigger worker node drain and reboot under I/O load on storage operators (dell-csm, portworx).
   Gate:   Volumes reattach within 30s without VolumeAttachment timeout.
 Step 4 [Fleet Canary Deployment]:
   Action: Roll out upgrade to 1 non-prod lab cluster before scheduling production fleet windows.
   Gate:   ClusterVersion reaches Available=True with 0 cluster operator degraded alerts for 48 hours.

--- [HUMAN-IN-THE-LOOP SIGN-OFF GATE] ---
 Status: PENDING_APPROVAL
 Required Approvers: TestOps Lead, Cloud Platform SRE Lead, Storage Administrator
 Checklist:
   [ ] All active VM migrations on mtv paused / drained
   [ ] Sandbox failover test passed on dell-csm, portworx
   [ ] TestOps qualification test suite executed on target build in staging
   [ ] Maintenance window approved by Change Advisory Board (CAB)
```

---

## 4. GitOps Pull Request Automation Bot

### Scenario A: Successful PR Manifest Dry-Run (Verdict: GO)

Bumping cluster `east-prod-01` to `4.22.8` modifies Red Hat Advanced Cluster Management (RHACM) `ClusterCurator` CRs using round-trip `ruamel.yaml`:

```bash
$ python run_gitops_pr.py --cluster east-prod-01 --target 4.22.8 --dry-run
```

#### Live Terminal Execution Output:

```text
2026-08-17 07:57:58 INFO gitops.bot: [DRY-RUN] Simulating GitOps PR creation for east-prod-01 -> 4.22.8
2026-08-17 07:57:58 INFO gitops.bot: Created new ClusterCurator manifest at clusters/east-prod-01/cluster-curator.yaml
{
  "action": "dry-run-preview",
  "cluster": "east-prod-01",
  "current_version": "4.22.2",
  "target_version": "4.22.8",
  "verdict": "go",
  "branch": "upgrade/east-prod-01-to-4.22.8",
  "base_branch": "main",
  "draft": false,
  "pr_title": "feat(gitops): upgrade east-prod-01 to OCP 4.22.8 [GO]",
  "pr_body": "## :robot: Automated Pre-Upgrade Assessment — east-prod-01\n\nThis Pull Request proposes bumping cluster **`east-prod-01`** OCP target from **`4.22.2`** to **`4.22.8`**.\n\n| Parameter | Value |\n| :--- | :--- |\n| **Cluster** | `east-prod-01` |\n| **Current Version** | `4.22.2` |\n| **Target Version** | `4.22.8` |\n| **Assessment Verdict** | **GO** :white_check_mark: |\n| **Assessment ID** | `#10` |\n| **Evaluated At** | `2026-08-16 23:10:59.647539+05:30` |\n\n### :white_check_mark: Validated Compatibility Checks\n\n- Upgrade path from 4.22.2 to 4.22.8 exists in Cincinnati graph.\n- Operator 'mtv' version 2.8.0 verified compatible with 4.22.8.\n- Operator 'dell-csm' version 1.11.0 verified compatible with 4.22.8.\n- Operator 'portworx' version 25.3.0 verified compatible with 4.22.8.\n\n### :clipboard: Pre-Merge Checklist\n- [ ] Verify disconnected/air-gapped release payload mirroring if applicable\n- [ ] Ensure active VM migrations (MTV) are quiescent before initiating node drains\n- [ ] Validate CSI storage replication & backup health (Dell CSM / Portworx)\n- [ ] Confirm maintenance window approval with TestOps / Release Engineering\n\n---\n*Automated by [OCV Upgrade & Migration Assessment Agent](https://github.com/openshift-virtualization/ocv-upgrade-agent)*",
  "modified_files": [
    "clusters/east-prod-01/cluster-curator.yaml"
  ],
  "diff": "diff --git a/clusters/east-prod-01/cluster-curator.yaml b/clusters/east-prod-01/cluster-curator.yaml\nnew file mode 100644\nindex 0000000..b363f93\n--- /dev/null\n+++ b/clusters/east-prod-01/cluster-curator.yaml\n@@ -0,0 +1,13 @@\n+apiVersion: cluster.open-cluster-management.io/v1beta1\n+kind: ClusterCurator\n+metadata:\n+  name: east-prod-01\n+  namespace: east-prod-01\n+  labels:\n+    open-cluster-management.io/cluster-name: east-prod-01\n+spec:\n+  desiredCuration: upgrade\n+  upgrade:\n+    channel: stable-4.22\n+    desiredUpdate: 4.22.8\n+    upstream: http://cincinnati.internal.net/api/upgrades_info/v1/graph\n"
}
```

---

### Scenario B: Strict Assessment Gating & Refusal (Verdict: NO-GO)

When attempting to open a GitOps PR against an unsafe target (`5.0.0`), the bot inspects the database assessment, refuses the request, prints all blocking reasons, and terminates with exit code 1 before any git operations or API calls:

```bash
$ python run_gitops_pr.py --cluster east-prod-01 --target 5.0.0 --dry-run
```

#### Live Terminal Execution Output:

```text
2026-08-17 08:10:19,200 ERROR __main__: Verdict is NO-GO for east-prod-01 -> 5.0.0 -- refusing to open a PR.
2026-08-17 08:10:19,200 ERROR __main__:   blocking: Blocker: No direct upgrade path found in Cincinnati graph from 4.22.2 to 5.0.0.
2026-08-17 08:10:19,200 ERROR __main__:   blocking: Blocker: Operator 'mtv' version 2.8.0 is incompatible with target OCP 5.0.0 (supported range: 4.18 to 4.22).
2026-08-17 08:10:19,200 ERROR __main__:   blocking: Blocker: Operator 'dell-csm' version 1.11.0 is incompatible with target OCP 5.0.0 (supported range: 4.18 to 4.22).
2026-08-17 08:10:19,200 ERROR __main__:   blocking: Blocker: Operator 'portworx' version 25.3.0 is incompatible with target OCP 5.0.0 (supported range: 4.16 to 4.22).
[Exit Code: 1]
```

---

## 5. Automated Test Suite Results

All 19 unit tests execute against offline fixtures and pass cleanly:

```bash
$ pytest
```

```text
============================= test session starts =============================
platform win32 -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\SRIMANDARBHA\Projects\ocv-upgrade-agent\ocv-upgrade-agent
collected 19 items

tests\test_cincinnati.py ..                                              [ 10%]
tests\test_cluster_state.py ..                                           [ 21%]
tests\test_gitops.py ......                                              [ 52%]
tests\test_lifecycle.py ..                                               [ 63%]
tests\test_redhat_security.py ...                                        [ 78%]
tests\test_release_info.py ..                                            [ 89%]
tests\test_vendor_matrix.py ..                                           [100%]

============================= 19 passed in 2.38s ==============================
```
```

---

### `README.md`

```markdown
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
  models.py                    SQLAlchemy models (Postgres + SQLite portable)
  db.py                        Engine & session factory, auto-loads .env
collectors/
  redhat_security.py           CVE + CSAF/errata -> advisories
  lifecycle.py                 GA/EOL dates      -> product_lifecycle
  cincinnati.py                Upgrade graph + conditional risks -> upgrade_edges
  cluster_state.py             Live ClusterVersion + CSVs -> component_versions
  vendor_matrix.py             Curated MTV, Dell CSM, Portworx data -> operator_compat
  release_info.py              `oc adm release info` pullspecs -> release_images
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
```

---

### `collectors/__init__.py`

```python

```

---

### `collectors/cincinnati.py`

```python
"""Cincinnati/OSUS graph collector -> upgrade_edges table.

Public endpoint (bastion use):
    https://api.openshift.com/api/upgrades_info/v1/graph?channel=stable-4.22&arch=amd64
    (requires `Accept: application/json`)

Disconnected/local OSUS (real fleet use -- get the base URL with):
    oc -n openshift-update-service get updateservice/osus \\
        -o jsonpath='{.status.policyEngineURI}'

Point CINCINNATI_URL at whichever one applies; this module doesn't care which,
it just needs a base URL that serves the same `/api/upgrades_info/v1/graph`
contract. Querying your own OSUS is what you want for the graph shape that
actually reflects your mirrored release set.

Graph shape: {"nodes": [...], "edges": [[i, j], ...], "conditionalEdges": [...]}
`edges` are unconditional (index pairs into `nodes`); `conditionalEdges` carry
a `risks` list, each with a human-readable message and a PromQL matchingRule
-- this is reference data (which risks exist for this edge), not a verdict for
any specific cluster. For "does this risk actually apply to *my* cluster",
read the live ClusterVersion object instead -- see cluster_state.py.
"""
from __future__ import annotations

import argparse
import logging
import os

import requests
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from db.db import get_session
from db.models import UpgradeEdge

log = logging.getLogger(__name__)

PUBLIC_CINCINNATI_URL = "https://api.openshift.com"
DEFAULT_CHANNELS = ["stable-4.21", "stable-4.22"]


def fetch_graph(
    channel: str,
    arch: str = "amd64",
    base_url: str | None = None,
    session: requests.Session | None = None,
) -> dict:
    base_url = base_url or os.environ.get("CINCINNATI_URL", PUBLIC_CINCINNATI_URL)
    http = session or requests
    resp = http.get(
        f"{base_url.rstrip('/')}/api/upgrades_info/v1/graph",
        params={"channel": channel, "arch": arch},
        headers={"Accept": "application/json"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def parse_edges(graph: dict, channel: str, arch: str) -> list[dict]:
    nodes = graph.get("nodes", [])
    versions = [n.get("version") for n in nodes]
    rows: list[dict] = []

    for pair in graph.get("edges", []):
        if len(pair) != 2:
            continue
        i, j = pair
        if i >= len(versions) or j >= len(versions):
            continue
        rows.append(
            {
                "channel": channel,
                "arch": arch,
                "from_version": versions[i],
                "to_version": versions[j],
                "conditional": False,
                "risk_name": None,
                "risk_message": None,
                "matching_rule": None,
            }
        )

    for cond in graph.get("conditionalEdges", []):
        edges = cond.get("edges", [])
        risks = cond.get("risks", [])
        for edge in edges:
            frm, to = edge.get("from"), edge.get("to")
            if not risks:
                rows.append(
                    {
                        "channel": channel,
                        "arch": arch,
                        "from_version": frm,
                        "to_version": to,
                        "conditional": True,
                        "risk_name": None,
                        "risk_message": None,
                        "matching_rule": None,
                    }
                )
            for risk in risks:
                rows.append(
                    {
                        "channel": channel,
                        "arch": arch,
                        "from_version": frm,
                        "to_version": to,
                        "conditional": True,
                        "risk_name": risk.get("name"),
                        "risk_message": risk.get("message"),
                        "matching_rule": risk.get("matchingRules"),
                    }
                )
    return rows


def upsert_edges(session: Session, rows: list[dict]) -> int:
    if not rows:
        return 0
    dialect = session.get_bind().dialect.name
    insert_fn = pg_insert if dialect == "postgresql" else sqlite_insert
    stmt = insert_fn(UpgradeEdge).values(rows)
    update_cols = {
        c: getattr(stmt.excluded, c)
        for c in rows[0]
        if c not in ("channel", "arch", "from_version", "to_version", "risk_name")
    }
    stmt = stmt.on_conflict_do_update(
        index_elements=["channel", "arch", "from_version", "to_version", "risk_name"],
        set_=update_cols,
    )
    session.execute(stmt)
    return len(rows)


def collect(channels: list[str] | None = None, arch: str = "amd64", base_url: str | None = None) -> int:
    channels = channels or DEFAULT_CHANNELS
    total = 0
    with get_session() as db:
        for channel in channels:
            try:
                graph = fetch_graph(channel, arch=arch, base_url=base_url)
            except requests.RequestException as exc:
                log.warning("Graph fetch failed for channel %s: %s", channel, exc)
                continue
            rows = parse_edges(graph, channel, arch)
            total += upsert_edges(db, rows)
    return total


def main():
    logging.basicConfig(level=logging.INFO)
    ap = argparse.ArgumentParser(description="Pull the Cincinnati/OSUS upgrade graph")
    ap.add_argument("--channel", action="append", help="repeatable, e.g. stable-4.22")
    ap.add_argument("--arch", default="amd64")
    ap.add_argument("--base-url", help="defaults to $CINCINNATI_URL, then the public API")
    args = ap.parse_args()
    n = collect(channels=args.channel, arch=args.arch, base_url=args.base_url)
    log.info("Upserted %d upgrade edges", n)


if __name__ == "__main__":
    main()
```

---

### `collectors/cluster_state.py`

```python
"""Live cluster collector -> component_versions table (+ raw conditional-update
data available to the compatibility engine).

Reads two things directly off each cluster rather than re-deriving them:

1. The `ClusterVersion` object (config.openshift.io/v1, cluster-scoped,
   name "version"). Its `status.conditionalUpdates[].risks[]` is the CVO's own
   PromQL-evaluated answer to "does this known risk apply to *this* cluster" --
   there's no PromQL to reimplement here, just read the field.
2. Installed `ClusterServiceVersion` objects (operators.coreos.com/v1alpha1,
   namespaced), filtered to the components you care about, to get installed
   OCV / Dell CSM / Portworx versions.

Fetch and parse are kept separate on purpose: parse_clusterversion() and
parse_csvs() are pure functions you can unit-test against a saved fixture
without a live cluster (see tests/test_cluster_state.py).

Auth: this expects a kubeconfig with a context per cluster (set
clusters.kubeconfig_context in your inventory) or, if run from inside a hub
cluster with RHACM, you'd swap fetch_clusterversion/fetch_csvs for calls
against the ACM Search API instead -- the parse functions don't change.
"""
from __future__ import annotations

import argparse
import logging
import re

from kubernetes import client, config

from db.db import get_session
from db.models import ComponentVersion, Cluster

log = logging.getLogger(__name__)

CV_GROUP, CV_VERSION, CV_PLURAL = "config.openshift.io", "v1", "clusterversions"
CSV_GROUP, CSV_VERSION, CSV_PLURAL = "operators.coreos.com", "v1alpha1", "clusterserviceversions"

# component key -> regex matched against CSV metadata.name
COMPONENT_CSV_PATTERNS: dict[str, re.Pattern] = {
    "ocv": re.compile(r"^kubevirt-hyperconverged-operator\."),
    "dell-csm": re.compile(r"^dell-csm-operator\."),
    "portworx": re.compile(r"^portworx-(operator|certified)\."),
}


def load_api_clients(context: str | None = None, kubeconfig_path: str | None = None):
    config.load_kube_config(config_file=kubeconfig_path, context=context)
    return client.CustomObjectsApi()


def fetch_clusterversion(api: "client.CustomObjectsApi") -> dict:
    return api.get_cluster_custom_object(CV_GROUP, CV_VERSION, CV_PLURAL, "version")


def fetch_csvs(api: "client.CustomObjectsApi") -> list[dict]:
    result = api.list_cluster_custom_object(CSV_GROUP, CSV_VERSION, CSV_PLURAL)
    return result.get("items", [])


def parse_clusterversion(cv: dict) -> dict:
    status = cv.get("status", {})
    desired = status.get("desired", {})
    return {
        "version": desired.get("version"),
        "channel": cv.get("spec", {}).get("channel"),
        "available_updates": status.get("availableUpdates") or [],
        "conditional_updates": status.get("conditionalUpdates") or [],
    }


def parse_csvs(csvs: list[dict]) -> list[dict]:
    """Return one row per recognized component: {component, version, namespace, csv_name}."""
    rows = []
    for csv in csvs:
        name = csv.get("metadata", {}).get("name", "")
        namespace = csv.get("metadata", {}).get("namespace")
        phase = csv.get("status", {}).get("phase")
        if phase and phase != "Succeeded":
            continue  # skip installs that aren't actually healthy
        for component, pattern in COMPONENT_CSV_PATTERNS.items():
            if pattern.match(name):
                version = csv.get("spec", {}).get("version")
                if not version and ".v" in name:
                    version = name.split(".v", 1)[1]
                rows.append(
                    {
                        "component": component,
                        "version": version or "unknown",
                        "namespace": namespace,
                        "csv_name": name,
                    }
                )
    return rows


def upsert_component_versions(session, cluster_id: int, rows: list[dict]) -> int:
    for row in rows:
        existing = (
            session.query(ComponentVersion)
            .filter_by(cluster_id=cluster_id, component=row["component"])
            .one_or_none()
        )
        if existing:
            existing.version = row["version"]
            existing.namespace = row["namespace"]
            existing.csv_name = row["csv_name"]
        else:
            session.add(ComponentVersion(cluster_id=cluster_id, **row))
    # always keep the ocp entry current too
    return len(rows)


def collect_for_cluster(cluster_name: str, kubeconfig_path: str | None = None) -> int:
    with get_session() as db:
        cluster = db.query(Cluster).filter_by(name=cluster_name).one_or_none()
        if cluster is None:
            log.warning("Cluster %s not found in inventory; skipping", cluster_name)
            return 0
        try:
            api = load_api_clients(context=cluster.kubeconfig_context, kubeconfig_path=kubeconfig_path)
            cv = parse_clusterversion(fetch_clusterversion(api))
            csv_rows = parse_csvs(fetch_csvs(api))
        except Exception as exc:  # noqa: BLE001 - a single unreachable cluster shouldn't kill the run
            log.warning("Could not collect from %s: %s", cluster_name, exc)
            return 0

        if cv.get("version"):
            cluster.ocp_version = cv["version"]
            csv_rows.append(
                {"component": "ocp", "version": cv["version"], "namespace": None, "csv_name": None}
            )
        n = upsert_component_versions(db, cluster.id, csv_rows)
        # Conditional-update risk data is per-cluster and time-sensitive; hand it
        # straight to the compatibility engine rather than persisting it here --
        # see engine/compatibility.py (next milestone) for where this goes.
        log.info(
            "%s: %d component rows, %d conditional-update risks currently reported",
            cluster_name, n, len(cv.get("conditional_updates", [])),
        )
        return n


def collect(cluster_names: list[str] | None = None, kubeconfig_path: str | None = None) -> int:
    with get_session() as db:
        names = cluster_names or [c.name for c in db.query(Cluster).all()]
    total = 0
    for name in names:
        total += collect_for_cluster(name, kubeconfig_path=kubeconfig_path)
    return total


def main():
    logging.basicConfig(level=logging.INFO)
    ap = argparse.ArgumentParser(description="Collect live ClusterVersion + operator state per cluster")
    ap.add_argument("--cluster", action="append", help="repeatable; default: every cluster in inventory")
    ap.add_argument("--kubeconfig", help="path to a kubeconfig with a context per cluster")
    args = ap.parse_args()
    n = collect(cluster_names=args.cluster, kubeconfig_path=args.kubeconfig)
    log.info("Upserted %d component_versions rows total", n)


if __name__ == "__main__":
    main()
```

---

### `collectors/lifecycle.py`

```python
"""Red Hat Product Lifecycle API collector -> product_lifecycle table.

Endpoint: https://access.redhat.com/product-life-cycles/api/v1/products?name=...
Docs:     https://access.redhat.com/articles/7074176

The API returns a list of {name, version, phase: [{name, date}, ...]} objects
-- phase is a list of named milestones rather than fixed keys, so
`_extract_phase_dates` matches on phase-name substrings. If Red Hat renames a
phase, that one field falls back to None rather than breaking the run.
"""
from __future__ import annotations

import argparse
import logging
from datetime import date, datetime

import requests
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from db.db import get_session
from db.models import ProductLifecycle

log = logging.getLogger(__name__)

LIFECYCLE_ENDPOINT = "https://access.redhat.com/product-life-cycles/api/v1/products"

# component key -> the product name(s) the Lifecycle API expects
DEFAULT_PRODUCTS = {
    "ocp": "Openshift Container Platform 4",
}

_PHASE_MAP = {
    "ga_date": ("general availability",),
    "full_support_end": ("full support",),
    "maintenance_end": ("maintenance support",),
    "eol_date": ("end of life", "retired"),
}


def fetch_lifecycle(product_name: str, session: requests.Session | None = None) -> list[dict]:
    http = session or requests
    resp = http.get(LIFECYCLE_ENDPOINT, params={"name": product_name}, timeout=30)
    resp.raise_for_status()
    payload = resp.json()
    return payload.get("data", payload if isinstance(payload, list) else [])


def _parse_date(value) -> date | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.strptime(str(value)[: len(fmt) - 2] if "T" not in fmt else str(value), fmt).date()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).date()
    except ValueError:
        log.debug("Unparseable lifecycle date: %r", value)
        return None


def _extract_phase_dates(phases: list[dict]) -> dict:
    out = {k: None for k in _PHASE_MAP}
    for entry in phases or []:
        name = (entry.get("name") or "").strip().lower()
        d = _parse_date(entry.get("date"))
        for field, needles in _PHASE_MAP.items():
            if any(n in name for n in needles) and d:
                out[field] = d
    return out


def _parse_item(item: dict, component: str) -> dict:
    dates = _extract_phase_dates(item.get("phase") or item.get("phases") or [])
    return {
        "component": component,
        "version": item.get("version") or item.get("name", "unknown"),
        "phase": item.get("current_phase") or item.get("type"),
        **dates,
    }


def upsert_lifecycle(session: Session, rows: list[dict]) -> int:
    if not rows:
        return 0
    dialect = session.get_bind().dialect.name
    insert_fn = pg_insert if dialect == "postgresql" else sqlite_insert
    stmt = insert_fn(ProductLifecycle).values(rows)
    update_cols = {c: getattr(stmt.excluded, c) for c in rows[0] if c not in ("component", "version")}
    stmt = stmt.on_conflict_do_update(index_elements=["component", "version"], set_=update_cols)
    session.execute(stmt)
    return len(rows)


def collect(products: dict[str, str] | None = None) -> int:
    products = products or DEFAULT_PRODUCTS
    total = 0
    with get_session() as db:
        for component, product_name in products.items():
            try:
                items = fetch_lifecycle(product_name)
            except requests.RequestException as exc:
                log.warning("Lifecycle fetch failed for %s: %s", product_name, exc)
                continue
            rows = [_parse_item(i, component) for i in items]
            total += upsert_lifecycle(db, rows)
    return total


def main():
    logging.basicConfig(level=logging.INFO)
    ap = argparse.ArgumentParser(description="Pull Red Hat Product Lifecycle dates")
    ap.parse_args()
    n = collect()
    log.info("Upserted %d lifecycle rows", n)


if __name__ == "__main__":
    main()
```

---

### `collectors/redhat_security.py`

```python
"""Red Hat Security Data API collector -> advisories table.

Covers the two feeds from your pre-check doc:
    CVE endpoint : https://access.redhat.com/hydra/rest/securitydata/cve.json
    CSAF/errata  : https://access.redhat.com/hydra/rest/securitydata/csaf.json

Both are public, unauthenticated JSON endpoints reachable from your bastion.
Run this on the connected side; ship the resulting DB rows (or a JSON export,
see `export_since()`) across the air gap through your normal mirror pipeline.

NOTE ON FIELD NAMES: this parses the response shape Red Hat documents at
https://access.redhat.com/solutions/6979472. Hydra's JSON responses have
drifted slightly between API generations before, so the first time you point
this at a live endpoint, log one raw response and diff it against
`_parse_cve_item` / `_parse_csaf_item` below -- both are written defensively
(`.get()` everywhere) specifically so a missing/renamed field degrades to
`None` instead of throwing.
"""
from __future__ import annotations

import argparse
import logging
from datetime import datetime, timezone

import requests
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from db.db import get_session
from db.models import Advisory

log = logging.getLogger(__name__)

CVE_ENDPOINT = "https://access.redhat.com/hydra/rest/securitydata/cve.json"
CSAF_ENDPOINT = "https://access.redhat.com/hydra/rest/securitydata/csaf.json"

# Products worth tracking for an OCV (OpenShift Virtualization) + Dell CSM +
# Portworx fleet. Extend as your operator inventory grows.
DEFAULT_PRODUCTS = [
    "openshift-container-platform",
    "openshift-virtualization",
]


def fetch_cves(
    product: str,
    severity: str | None = None,
    after: str | None = None,
    session: requests.Session | None = None,
) -> list[dict]:
    """GET the CVE feed for one product, optionally filtered by severity/date."""
    params = {"product": product}
    if severity:
        params["severity"] = severity
    if after:
        params["after"] = after
    http = session or requests
    resp = http.get(CVE_ENDPOINT, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_csaf(
    severity: str | None = None,
    after: str | None = None,
    session: requests.Session | None = None,
) -> list[dict]:
    """GET the CSAF/errata index, optionally filtered by severity/date."""
    params = {}
    if severity:
        params["severity"] = severity
    if after:
        params["after"] = after
    http = session or requests
    resp = http.get(CSAF_ENDPOINT, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _parse_dt(value) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def _parse_cve_item(item: dict, affected_component: str) -> dict:
    return {
        "source": "redhat-cve",
        "external_id": item.get("CVE") or item.get("cve") or item.get("id", "UNKNOWN"),
        "title": item.get("bugzilla", {}).get("description") or item.get("CVE", "CVE"),
        "severity": (item.get("severity") or item.get("threat_severity") or "").lower() or None,
        "affected_component": affected_component,
        "affected_version_range": None,  # filled in by operator_compat cross-reference downstream
        "published_at": _parse_dt(item.get("public_date")),
        "url": item.get("resource_url"),
        "raw": item,
    }


def _parse_csaf_item(item: dict, affected_component: str) -> dict:
    csaf_id = item.get("RHSA") or item.get("id") or item.get("CVE") or item.get("name") or "UNKNOWN"
    title = item.get("title") or item.get("RHSA") or csaf_id
    pub_date = item.get("released_on") or item.get("current_release_date") or item.get("initial_release_date")
    url = item.get("resource_url") or item.get("self_href") or f"https://access.redhat.com/errata/{csaf_id}"
    return {
        "source": "redhat-errata",
        "external_id": csaf_id,
        "title": title,
        "severity": (item.get("severity") or "").lower() or None,
        "affected_component": affected_component,
        "affected_version_range": None,
        "published_at": _parse_dt(pub_date),
        "url": url,
        "raw": item,
    }


def upsert_advisories(session: Session, rows: list[dict]) -> int:
    """Upsert on (source, external_id). Returns count written."""
    if not rows:
        return 0
    dialect = session.get_bind().dialect.name
    insert_fn = pg_insert if dialect == "postgresql" else sqlite_insert
    stmt = insert_fn(Advisory).values(rows)
    update_cols = {c: getattr(stmt.excluded, c) for c in rows[0] if c not in ("source", "external_id")}
    stmt = stmt.on_conflict_do_update(
        index_elements=["source", "external_id"], set_=update_cols
    )
    session.execute(stmt)
    return len(rows)


def collect(products: list[str] | None = None, severity: str | None = None, after: str | None = None) -> int:
    products = products or DEFAULT_PRODUCTS
    total = 0
    with get_session() as db:
        for product in products:
            component = "ocv" if "virtualization" in product else "ocp"
            try:
                cves = fetch_cves(product, severity=severity, after=after)
            except requests.RequestException as exc:
                log.warning("CVE fetch failed for %s: %s", product, exc)
                continue
            rows = [_parse_cve_item(c, component) for c in cves]
            total += upsert_advisories(db, rows)

        try:
            errata = fetch_csaf(severity=severity, after=after)
            rows = [_parse_csaf_item(e, "ocp") for e in errata]
            total += upsert_advisories(db, rows)
        except requests.RequestException as exc:
            log.warning("CSAF fetch failed: %s", exc)
    return total


def main():
    logging.basicConfig(level=logging.INFO)
    ap = argparse.ArgumentParser(description="Pull Red Hat CVE/errata data into advisories table")
    ap.add_argument("--product", action="append", help="repeatable; default: OCP + OCV")
    ap.add_argument("--severity", choices=["low", "moderate", "important", "critical"])
    ap.add_argument("--after", help="YYYY-MM-DD; only advisories published after this date")
    args = ap.parse_args()
    n = collect(products=args.product, severity=args.severity, after=args.after)
    log.info("Upserted %d advisories", n)


if __name__ == "__main__":
    main()
```

---

### `collectors/release_info.py`

```python
"""`oc adm release info` collector -> release_images table.

Covers point 5/6 from your original pre-check doc for a disconnected
environment: inspecting a mirrored release payload directly instead of
scraping web pages. Two things intentionally kept separate:

- `-o json` gives a stable, well-known structure (an OpenShift release
  payload's `references` field is literally an ImageStream) -- this is what
  we parse and persist, as `release_images`, for feeding an image vulnerability
  scanner per component.

- `--commits <from> <to>` gives a human-readable component-by-component commit
  diff. Its exact column layout isn't a documented/stable contract the way the
  JSON output is, so this module surfaces the raw text for a human to read (or
  paste into a PR description) rather than parsing it into DB rows -- for a
  structured "what bugs did this fix" answer, cross-reference the
  `redhat-errata` rows from redhat_security.py instead, since RHBA/RHSA
  content is the actual source of truth for that.
"""
from __future__ import annotations

import argparse
import json
import logging
import subprocess

from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from db.db import get_session
from db.models import ReleaseImage

log = logging.getLogger(__name__)


def fetch_release_metadata(version: str, oc_binary: str = "oc") -> dict:
    proc = subprocess.run(
        [oc_binary, "adm", "release", "info", version, "-o", "json"],
        capture_output=True, text=True, timeout=120,
    )
    proc.check_returncode()
    return json.loads(proc.stdout)


def fetch_commits_raw(from_version: str, to_version: str, oc_binary: str = "oc") -> str:
    """Human-readable component commit diff -- not parsed, just returned as text."""
    proc = subprocess.run(
        [oc_binary, "adm", "release", "info", from_version, to_version, "--commits"],
        capture_output=True, text=True, timeout=120,
    )
    proc.check_returncode()
    return proc.stdout


def parse_release_images(metadata: dict) -> list[dict]:
    version = metadata.get("metadata", {}).get("version", "unknown")
    tags = metadata.get("references", {}).get("spec", {}).get("tags", [])
    rows = []
    for tag in tags:
        image = (tag.get("from") or {}).get("name")
        component = tag.get("name")
        if component and image:
            rows.append({"component": component, "version": version, "image": image})
    return rows


def upsert_release_images(session: Session, rows: list[dict]) -> int:
    if not rows:
        return 0
    dialect = session.get_bind().dialect.name
    insert_fn = pg_insert if dialect == "postgresql" else sqlite_insert
    stmt = insert_fn(ReleaseImage).values(rows)
    update_cols = {c: getattr(stmt.excluded, c) for c in rows[0] if c not in ("version", "component")}
    stmt = stmt.on_conflict_do_update(index_elements=["version", "component"], set_=update_cols)
    session.execute(stmt)
    return len(rows)


def collect(versions: list[str] | str | None = None, oc_binary: str = "oc") -> int:
    if not versions:
        log.info("No target release version provided for release-info collector; skipping.")
        return 0
    if isinstance(versions, str):
        versions = [versions]

    total = 0
    with get_session() as db:
        for version in versions:
            try:
                metadata = fetch_release_metadata(version, oc_binary=oc_binary)
            except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError) as exc:
                log.warning("release info failed for %s: %s", version, exc)
                continue
            rows = parse_release_images(metadata)
            total += upsert_release_images(db, rows)
    return total


def main():
    logging.basicConfig(level=logging.INFO)
    ap = argparse.ArgumentParser(description="Collect release image inventory via `oc adm release info`")
    ap.add_argument("version", help="release payload version/pullspec to inspect")
    ap.add_argument("--oc-binary", default="oc")
    ap.add_argument(
        "--commits-from", help="if set (with --commits-to), print the raw commit diff and exit"
    )
    ap.add_argument("--commits-to")
    args = ap.parse_args()

    if args.commits_from and args.commits_to:
        print(fetch_commits_raw(args.commits_from, args.commits_to, oc_binary=args.oc_binary))
        return

    n = collect(args.version, oc_binary=args.oc_binary)
    log.info("Upserted %d release_images rows for %s", n, args.version)


if __name__ == "__main__":
    main()
```

---

### `collectors/vendor_matrix.py`

```python
"""Vendor support-matrix loader -> operator_compat + advisories.

Dell and Portworx don't expose their OCP compatibility data as an API --
Dell's matrix lives at https://dell.github.io/csm-docs/docs/supportmatrix/
and Portworx's known-bug-per-version data lives in their operator release
notes (https://docs.portworx.com/portworx-enterprise/operator-release-notes).
Both are docs sites, not APIs, so this is intentionally a *reviewed* pattern
rather than a live scraper:

    data/vendor_matrix_seed.yaml  (git-tracked, PR-reviewed like any config
                                    change)  --->  this loader  --->  DB

Update the YAML by hand (or via a separate, human-reviewed diff-checker job)
whenever a vendor ships a new release; this module just does the upsert.
It's seeded with a couple of real, currently-published examples to show the
expected shape -- treat those as a starting point, not a complete matrix.
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

import yaml
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from db.db import get_session
from db.models import Advisory, OperatorCompat

log = logging.getLogger(__name__)

DEFAULT_SEED_PATH = Path(__file__).resolve().parent.parent / "data" / "vendor_matrix_seed.yaml"


def load_seed(path: Path | None = None) -> dict:
    path = path or DEFAULT_SEED_PATH
    with open(path) as fh:
        data = yaml.safe_load(fh) or {}
    data.setdefault("operator_compat", [])
    data.setdefault("known_bugs", [])
    return data


def _upsert(session: Session, model, rows: list[dict], conflict_cols: list[str]) -> int:
    if not rows:
        return 0
    dialect = session.get_bind().dialect.name
    insert_fn = pg_insert if dialect == "postgresql" else sqlite_insert
    stmt = insert_fn(model).values(rows)
    update_cols = {c: getattr(stmt.excluded, c) for c in rows[0] if c not in conflict_cols}
    stmt = stmt.on_conflict_do_update(index_elements=conflict_cols, set_=update_cols)
    session.execute(stmt)
    return len(rows)


def collect(path: Path | None = None) -> tuple[int, int]:
    seed = load_seed(path)
    compat_rows = [
        {
            "component": e["component"],
            "operator_version": str(e["operator_version"]),
            "min_ocp": e.get("min_ocp"),
            "max_ocp": e.get("max_ocp"),
            "source": f"{e['component']}-support-matrix",
            "notes": e.get("notes"),
        }
        for e in seed["operator_compat"]
    ]
    bug_rows = [
        {
            "source": e["component"],
            "external_id": e["external_id"],
            "title": e["title"],
            "severity": e.get("severity"),
            "affected_component": e["component"],
            "affected_version_range": e.get("affected_version_range"),
            "published_at": e.get("published_at"),
            "url": e.get("url"),
            "raw": e,
        }
        for e in seed["known_bugs"]
    ]

    with get_session() as db:
        n_compat = _upsert(db, OperatorCompat, compat_rows, ["component", "operator_version", "source"])
        n_bugs = _upsert(db, Advisory, bug_rows, ["source", "external_id"])
    return n_compat, n_bugs


def main():
    logging.basicConfig(level=logging.INFO)
    ap = argparse.ArgumentParser(description="Load curated Dell CSM / Portworx matrix data")
    ap.add_argument("--seed", type=Path, help=f"default: {DEFAULT_SEED_PATH}")
    args = ap.parse_args()
    n_compat, n_bugs = collect(args.seed)
    log.info("Upserted %d operator_compat rows, %d vendor advisories", n_compat, n_bugs)


if __name__ == "__main__":
    main()
```

---

### `data/gitops_targets.yaml`

```yaml
# GitOps repository targets and cluster curator mapping.
# Used by run_gitops_pr.py and gitops.bot to automate upgrade PRs.

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

  west-prod-01:
    cluster_path: "clusters/west-prod-01"
    curator_namespace: "west-prod-01"

  central-edge-01:
    cluster_path: "clusters/central-edge-01"
    curator_namespace: "central-edge-01"
```

---

### `data/testops_confluence_policy.md`

```markdown
# TestOps Confluence Policy: OpenShift & Virtualization Upgrade Standard

**Document ID:** TESTOPS-POL-4082  
**Owner:** Cloud Platform SRE & TestOps Engineering  
**Scope:** OpenShift Container Platform (OCP), OpenShift Virtualization (OCV), MTV, Dell CSM, Portworx  

---

## 1. Core Principles & Motive Hierarchy

1. **Migration Continuity Over Routine Upgrades (Higher Motive):**
   * During an active VMware-to-OCV migration wave using MTV (Migration Toolkit for Virtualization), **workload stability is paramount**.
   * Upgrades must **not** be performed simply to track the latest minor release unless:
     * A critical security vulnerability (RHSA Critical / Important CVE actively exploitable in disconnected env) requires it, OR
     * A critical bug affecting current migration throughput/cutover is fixed in the target release.

2. **Major Version Drift Policy (e.g., OCP 4 $\rightarrow$ 5 or Major API Deprecations):**
   * Any upgrade spanning a major version jump (or major Kubernetes API removal) requires an automatic **NO-GO (ESCALATED)**.
   * Rolling out major drift without a dedicated staging qualification run with active VM live-migration and CSI storage failover tests is strictly prohibited.

---

## 2. Mandatory TestOps Pre-Upgrade Gates

Before an upgrade PR can be merged or rolled out:

| Gate | Category | Description | Required Outcome |
| :--- | :--- | :--- | :--- |
| **G1: Migration Safety** | MTV / Forklift | No active in-flight VM migration plans in `Running` or `CutoverScheduled` state. | Zero active migrations during upgrade window. |
| **G2: Storage Driver Qualification** | Dell CSM / Portworx | Verified CSI node-driver pods, VolumeAttachment reconcilers, and RWX block storage failover on target OCP version in Sandbox. | All CSI sanity suites pass with 0 storage timeouts. |
| **G3: Live VM Migration Test** | OCV / KubeVirt | Conducted synthetic live migration of sample VM with dedicated virtio-win / linux drivers across worker nodes on target z-stream. | 0 dropped TCP packets, migration completes < 45s. |
| **G4: Operator Compatibility Matrix** | All Operators | MTV, Dell CSM, and Portworx versions are within certified `[min_ocp, max_ocp]` bounds. | 100% matrix compliance in database. |

---

## 3. Escalation & Human Sign-Off Requirements

When the upgrade agent detects:
* **Major Version Drift** (e.g., OCP 4.x to 5.x) OR
* **Incompatible MTV / Storage Operators** OR
* **Upgrades without Critical CVE justification during an active migration campaign**:

The agent must output a **NO-GO (ESCALATE)** status and provide:
1. Executive Synopsis of the risks.
2. Architectural analysis detailing what storage and migration components would break.
3. High-level Staging Qualification & Test Remediation Plan.
4. Formal Human Sign-Off template for Platform Lead / TestOps Lead approval.
```

---

### `data/vendor_matrix_seed.yaml`

```yaml
# Hand-curated MTV, Dell CSM, and Portworx compatibility + known-bug data.
# Source of truth for each entry is the vendor/Red Hat documentation.
# Loaded into operator_compat and advisories tables via collectors/vendor_matrix.py.

operator_compat:
  # ===========================================================================
  # MTV (Migration Toolkit for Virtualization / forklift-operator)
  # ===========================================================================
  - component: mtv
    operator_version: "2.6.0"
    min_ocp: "4.15"
    max_ocp: "4.17"
    source: "redhat-mtv-matrix"
    notes: >
      MTV 2.6.0 supported on OCP 4.15 to 4.17. Validated for VMware vSphere 7.x/8.x
      and OpenStack source migrations into OpenShift Virtualization.

  - component: mtv
    operator_version: "2.7.0"
    min_ocp: "4.16"
    max_ocp: "4.18"
    source: "redhat-mtv-matrix"
    notes: >
      MTV 2.7.0 adds support for warm migrations with changed block tracking (CBT)
      and OpenShift Virtualization 4.16+. Requires OCP <= 4.18.

  - component: mtv
    operator_version: "2.8.0"
    min_ocp: "4.18"
    max_ocp: "4.22"
    source: "redhat-mtv-matrix"
    notes: >
      MTV 2.8.x validated on OCP 4.18 through 4.22. Supports direct vSphere 8 U3
      migration plans with automated storage class mapping.

  # ===========================================================================
  # Dell CSM (Container Storage Modules)
  # ===========================================================================
  - component: dell-csm
    operator_version: "1.9"
    min_ocp: "4.17"
    max_ocp: "4.18"
    source: "dell-support-matrix"
    notes: >
      CSM Operator v1.9.x validated for CSM 1.14 on OCP 4.17 and 4.18.
      Covers PowerStore, PowerFlex, PowerScale, and PowerMax CSI drivers.

  - component: dell-csm
    operator_version: "1.11.0"
    min_ocp: "4.18"
    max_ocp: "4.22"
    source: "dell-support-matrix"
    notes: >
      CSM Operator v1.11.0 validated on OCP 4.18 through 4.22. Includes
      PowerStore CSI 2.11 with VolumeGroupSnapshot support for VM disks.

  - component: dell-csm
    operator_version: "1.12.0"
    min_ocp: "4.20"
    max_ocp: "4.22"
    source: "dell-support-matrix"
    notes: >
      CSM Operator v1.12.0 for OCP 4.20 to 4.22. Requires Dell CSI v2.12+.
      Does not support major release jumps (OCP 5.x) without CSI driver upgrade.

  # ===========================================================================
  # Portworx Enterprise Operator
  # ===========================================================================
  - component: portworx
    operator_version: "24.2.0"
    min_ocp: "4.14"
    max_ocp: "4.16"
    source: "portworx-support-matrix"
    notes: >
      Portworx Enterprise Operator 24.2 validated up to OCP 4.16.

  - component: portworx
    operator_version: "25.3.0"
    min_ocp: "4.16"
    max_ocp: "4.22"
    source: "portworx-support-matrix"
    notes: >
      Portworx Enterprise Operator 25.3.0 validated on OCP 4.16 through 4.22.
      Full support for OpenShift Virtualization live migration and sharedv4 RWX block volumes.

  - component: portworx
    operator_version: "26.1.0"
    min_ocp: "4.20"
    max_ocp: "4.22"
    source: "portworx-support-matrix"
    notes: >
      Portworx 26.1.0 for OCP 4.20 to 4.22. Requires kernel header alignment
      on CoreOS nodes. Major drift to OCP 5.x is unsupported without Portworx 27.x.

known_bugs:
  - component: mtv
    external_id: "MTV-1042"
    title: >
      Warm migration hangs during final cutover phase if OCP API server throttles
      virt-v2v controller status updates on OCP 4.22.3 - 4.22.5.
    severity: important
    affected_version_range: "2.6.0-2.7.0"
    url: "https://access.redhat.com/solutions/mtv-migration-cutover-bug"
    published_at: null
    workaround: >
      Upgrade MTV operator to 2.8.0 before upgrading target cluster beyond OCP 4.18.

  - component: dell-csm
    external_id: "DELL-CSM-4412"
    title: >
      PowerStore CSI driver intermittent volume detach timeout during node drain
      on OCP versions with Kubernetes 1.31+ kernel drift.
    severity: important
    affected_version_range: "<=1.9.0"
    url: "https://dell.github.io/csm-docs/docs/known-issues/"
    published_at: null
    workaround: >
      Upgrade Dell CSM operator to 1.11.0+ before initiating cluster upgrade.

  - component: portworx
    external_id: "PWX-46691"
    title: >
      Portworx-specific ServiceAccounts without annotations are updated on
      every reconciliation loop, triggering excessive Secret regeneration and
      OCP API traffic.
    severity: moderate
    affected_version_range: "<=4.15"
    url: "https://docs.portworx.com/portworx-enterprise/operator-release-notes"
    published_at: null
    workaround: >
      Add at least one annotation to each Portworx-specific ServiceAccount object;
      fixed going forward in Operator 25.3.0+.
```

---

### `db/__init__.py`

```python

```

---

### `db/db.py`

```python
"""Engine/session management.

DATABASE_URL examples:
    sqlite:///./ocv_agent.db                                   (local dev/tests)
    postgresql+psycopg2://user:pass@pg-host:5432/ocv_agent      (real deployment)
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from db.models import Base

DEFAULT_URL = "sqlite:///./ocv_agent.db"


def _load_env_file():
    """Load key=value pairs from .env if present without requiring external packages."""
    env_path = os.path.join(os.getcwd(), ".env")
    if not os.path.exists(env_path):
        return
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k and k not in os.environ:
                    os.environ[k] = v
    except OSError:
        pass


_load_env_file()


def make_engine(url: str | None = None):
    url = url or os.environ.get("DATABASE_URL", DEFAULT_URL)
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args, future=True)


_engine = None
_SessionLocal = None


def init_db(url: str | None = None, create_tables: bool = True):
    """Call once at startup (or let get_session() do it lazily)."""
    global _engine, _SessionLocal
    _engine = make_engine(url)
    _SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False, future=True)
    if create_tables:
        Base.metadata.create_all(_engine)
    return _engine


@contextmanager
def get_session() -> Iterator[Session]:
    global _SessionLocal
    if _SessionLocal is None:
        init_db()
    session = _SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

---

### `db/models.py`

```python
"""SQLAlchemy models mirroring db/schema.sql.

Uses the generic `JSON` type (not Postgres-specific JSONB) so the same models
work against SQLite for local dev/tests and Postgres in production -- see
schema.sql for the JSONB-flavored DDL used for the real deployment.
"""
from __future__ import annotations

import datetime as dt

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def _utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


class Cluster(Base):
    """Minimal stub -- replace with / point at your real cluster inventory table."""

    __tablename__ = "clusters"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    region: Mapped[str] = mapped_column(String)
    env: Mapped[str] = mapped_column(String, default="prod")
    ocp_version: Mapped[str] = mapped_column(String)
    api_url: Mapped[str | None] = mapped_column(String, nullable=True)
    kubeconfig_context: Mapped[str | None] = mapped_column(String, nullable=True)
    connected: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    component_versions: Mapped[list["ComponentVersion"]] = relationship(
        back_populates="cluster", cascade="all, delete-orphan"
    )


class ComponentVersion(Base):
    __tablename__ = "component_versions"
    __table_args__ = (UniqueConstraint("cluster_id", "component"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    cluster_id: Mapped[int] = mapped_column(ForeignKey("clusters.id", ondelete="CASCADE"))
    component: Mapped[str] = mapped_column(String)  # ocp | ocv | dell-csm | portworx | ...
    version: Mapped[str] = mapped_column(String)
    channel: Mapped[str | None] = mapped_column(String, nullable=True)
    namespace: Mapped[str | None] = mapped_column(String, nullable=True)
    csv_name: Mapped[str | None] = mapped_column(String, nullable=True)
    observed_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    cluster: Mapped["Cluster"] = relationship(back_populates="component_versions")


class Advisory(Base):
    __tablename__ = "advisories"
    __table_args__ = (UniqueConstraint("source", "external_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String)  # redhat-cve | redhat-errata | dell-csm | portworx
    external_id: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(Text)
    severity: Mapped[str | None] = mapped_column(String, nullable=True)
    affected_component: Mapped[str | None] = mapped_column(String, nullable=True)
    affected_version_range: Mapped[str | None] = mapped_column(String, nullable=True)
    published_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    url: Mapped[str | None] = mapped_column(String, nullable=True)
    fetched_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    raw: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class OperatorCompat(Base):
    __tablename__ = "operator_compat"
    __table_args__ = (UniqueConstraint("component", "operator_version", "source"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    component: Mapped[str] = mapped_column(String)
    operator_version: Mapped[str] = mapped_column(String)
    min_ocp: Mapped[str | None] = mapped_column(String, nullable=True)
    max_ocp: Mapped[str | None] = mapped_column(String, nullable=True)
    source: Mapped[str] = mapped_column(String)  # olm-catalog | dell-support-matrix | portworx-support-matrix
    verified_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class ProductLifecycle(Base):
    __tablename__ = "product_lifecycle"
    __table_args__ = (UniqueConstraint("component", "version"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    component: Mapped[str] = mapped_column(String)
    version: Mapped[str] = mapped_column(String)
    phase: Mapped[str | None] = mapped_column(String, nullable=True)
    ga_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    full_support_end: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    maintenance_end: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    eol_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    fetched_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class UpgradeEdge(Base):
    __tablename__ = "upgrade_edges"
    __table_args__ = (
        UniqueConstraint("channel", "arch", "from_version", "to_version", "risk_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    channel: Mapped[str] = mapped_column(String)
    arch: Mapped[str] = mapped_column(String, default="amd64")
    from_version: Mapped[str] = mapped_column(String)
    to_version: Mapped[str] = mapped_column(String)
    conditional: Mapped[bool] = mapped_column(Boolean, default=False)
    risk_name: Mapped[str | None] = mapped_column(String, nullable=True)
    risk_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    matching_rule: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    fetched_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class ReleaseImage(Base):
    __tablename__ = "release_images"
    __table_args__ = (UniqueConstraint("version", "component"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    component: Mapped[str] = mapped_column(String)
    version: Mapped[str] = mapped_column(String)
    image: Mapped[str] = mapped_column(String)
    fetched_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class Assessment(Base):
    """Written by the compatibility engine (next milestone)."""

    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(primary_key=True)
    cluster_id: Mapped[int] = mapped_column(ForeignKey("clusters.id", ondelete="CASCADE"))
    target_version: Mapped[str] = mapped_column(String)
    verdict: Mapped[str] = mapped_column(String)  # go | go-with-caveats | no-go
    reasons: Mapped[dict] = mapped_column(JSON)
    evaluated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class Alert(Base):
    """Written by the alerting engine (future milestone)."""

    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    fingerprint: Mapped[str] = mapped_column(String, unique=True)
    cluster_id: Mapped[int | None] = mapped_column(
        ForeignKey("clusters.id", ondelete="CASCADE"), nullable=True
    )
    advisory_id: Mapped[int | None] = mapped_column(
        ForeignKey("advisories.id", ondelete="CASCADE"), nullable=True
    )
    message: Mapped[str] = mapped_column(Text)
    first_seen: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    last_seen: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    acknowledged_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
```

---

### `db/schema.sql`

```sql
-- OCV upgrade agent — core schema (PostgreSQL)
--
-- This is organized in three groups:
--   1. Fleet inventory   (clusters, component_versions)      -- observed state
--   2. Reference data     (advisories, operator_compat,
--                          product_lifecycle, upgrade_edges)  -- filled by collectors/
--   3. Agent output        (assessments, alerts)              -- filled by the
--                                                                 compatibility/alerting
--                                                                 engine (next milestone)
--
-- `clusters` is a minimal stub: you almost certainly already have a real
-- cluster/version inventory table. Point component_versions.cluster_id at
-- your existing table's PK instead of this one -- it's only here so the
-- schema is runnable standalone for local dev/testing.

CREATE TABLE IF NOT EXISTS clusters (
    id                  SERIAL PRIMARY KEY,
    name                TEXT NOT NULL UNIQUE,
    region              TEXT NOT NULL,
    env                 TEXT NOT NULL DEFAULT 'prod',      -- prod | non-prod | lab
    ocp_version         TEXT NOT NULL,                     -- e.g. 4.20.11
    api_url             TEXT,
    kubeconfig_context  TEXT,                              -- context name in mounted kubeconfig
    connected           BOOLEAN NOT NULL DEFAULT FALSE,     -- true only for the bastion, generally false
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Observed component versions per cluster. One row per (cluster, component).
-- Populated by collectors/cluster_state.py from the live ClusterVersion object
-- and installed ClusterServiceVersions (CSVs).
CREATE TABLE IF NOT EXISTS component_versions (
    id              SERIAL PRIMARY KEY,
    cluster_id      INTEGER NOT NULL REFERENCES clusters(id) ON DELETE CASCADE,
    component       TEXT NOT NULL,      -- 'ocp' | 'ocv' | 'dell-csm' | 'portworx' | ...
    version         TEXT NOT NULL,
    channel         TEXT,
    namespace       TEXT,
    csv_name        TEXT,               -- OLM ClusterServiceVersion name, when OLM-managed
    observed_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (cluster_id, component)
);

-- Unified CVE / errata / vendor-bug feed. `source` tells you which collector
-- (and which trust level) an entry came from.
CREATE TABLE IF NOT EXISTS advisories (
    id                      SERIAL PRIMARY KEY,
    source                  TEXT NOT NULL,   -- 'redhat-cve' | 'redhat-errata' | 'dell-csm' | 'portworx'
    external_id             TEXT NOT NULL,   -- CVE-2026-31431 / RHSA-2026:1234 / PWX-46691
    title                   TEXT NOT NULL,
    severity                TEXT,            -- critical | important | moderate | low
    affected_component      TEXT,            -- 'ocp' | 'ocv' | 'dell-csm' | 'portworx'
    affected_version_range  TEXT,            -- free text: "<=4.15", "4.17-4.18", etc.
    published_at            TIMESTAMPTZ,
    url                     TEXT,
    fetched_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    raw                     JSONB,           -- original payload, for traceability
    UNIQUE (source, external_id)
);

-- Operator <-> OCP compatibility ranges, from OLM catalog metadata
-- (olm.maxOpenShiftVersion / com.redhat.openshift.versions) or curated vendor
-- support matrices (Dell, Portworx don't publish an API for this).
CREATE TABLE IF NOT EXISTS operator_compat (
    id                  SERIAL PRIMARY KEY,
    component           TEXT NOT NULL,
    operator_version    TEXT NOT NULL,
    min_ocp             TEXT,
    max_ocp             TEXT,
    source              TEXT NOT NULL,   -- 'olm-catalog' | 'dell-support-matrix' | 'portworx-support-matrix'
    verified_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    notes               TEXT,
    UNIQUE (component, operator_version, source)
);

-- GA / EOL windows from the Red Hat Product Lifecycle API.
CREATE TABLE IF NOT EXISTS product_lifecycle (
    id                  SERIAL PRIMARY KEY,
    component           TEXT NOT NULL,
    version             TEXT NOT NULL,
    phase               TEXT,        -- 'Full Support' | 'Maintenance Support' | 'EOL' ...
    ga_date             DATE,
    full_support_end    DATE,
    maintenance_end     DATE,
    eol_date            DATE,
    fetched_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (component, version)
);

-- Cincinnati/OSUS graph edges, including conditional-risk metadata, as served
-- by your local OSUS instance (or the public API for the bastion's cache).
CREATE TABLE IF NOT EXISTS upgrade_edges (
    id              SERIAL PRIMARY KEY,
    channel         TEXT NOT NULL,
    arch            TEXT NOT NULL DEFAULT 'amd64',
    from_version    TEXT NOT NULL,
    to_version      TEXT NOT NULL,
    conditional     BOOLEAN NOT NULL DEFAULT FALSE,
    risk_name       TEXT,
    risk_message    TEXT,
    matching_rule   JSONB,          -- the PromQL rule payload, kept for reference/audit
    fetched_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (channel, arch, from_version, to_version, risk_name)
);

-- Release image inventory (from `oc adm release info --pullspecs`), handy as
-- direct input to an image vulnerability scanner.
CREATE TABLE IF NOT EXISTS release_images (
    id          SERIAL PRIMARY KEY,
    component   TEXT NOT NULL,
    version     TEXT NOT NULL,
    image       TEXT NOT NULL,
    fetched_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (version, component)
);

-- ---------------------------------------------------------------------------
-- Everything below is written by the compatibility/alerting engine, which is
-- the next milestone -- included here so the schema is complete up front.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS assessments (
    id              SERIAL PRIMARY KEY,
    cluster_id      INTEGER NOT NULL REFERENCES clusters(id) ON DELETE CASCADE,
    target_version  TEXT NOT NULL,
    verdict         TEXT NOT NULL,      -- 'go' | 'go-with-caveats' | 'no-go'
    reasons         JSONB NOT NULL,
    evaluated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS alerts (
    id              SERIAL PRIMARY KEY,
    fingerprint     TEXT NOT NULL UNIQUE,
    cluster_id      INTEGER REFERENCES clusters(id) ON DELETE CASCADE,
    advisory_id     INTEGER REFERENCES advisories(id) ON DELETE CASCADE,
    message         TEXT NOT NULL,
    first_seen      TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen       TIMESTAMPTZ NOT NULL DEFAULT now(),
    acknowledged_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_advisories_component ON advisories (affected_component);
CREATE INDEX IF NOT EXISTS idx_operator_compat_component ON operator_compat (component);
CREATE INDEX IF NOT EXISTS idx_upgrade_edges_from ON upgrade_edges (channel, arch, from_version);
CREATE INDEX IF NOT EXISTS idx_component_versions_component ON component_versions (component);
```

---

### `engine/__init__.py`

```python
"""OCV Upgrade Compatibility Engine."""
```

---

### `engine/compatibility.py`

```python
"""Deterministic Upgrade Compatibility Engine (GO / GO-WITH-CAVEATS / NO-GO).

Evaluates concrete facts from the database (and optional live cluster state):
  1. Upgrade graph connectivity (Cincinnati / OSUS upgrade edges)
  2. Conditional upgrade risks (Multus, CNI, storage, etcd, etc.)
  3. Installed operator compatibility (Dell CSM, Portworx, OCV, etc.)
  4. Red Hat product lifecycle windows (GA, Full Support, Maintenance, EOL)
  5. Security advisories / critical bugs
"""
from __future__ import annotations

import datetime as dt
import logging
from typing import Any

from sqlalchemy.orm import Session

from db.models import Assessment, Cluster, ComponentVersion, OperatorCompat, ProductLifecycle, UpgradeEdge

log = logging.getLogger(__name__)


def parse_version_tuple(v: str | None) -> tuple[int, ...]:
    """Parse version string like '4.22.8' into (4, 22, 8) for numeric comparison."""
    if not v:
        return ()
    parts = []
    # Strip prefixes like 'v' or 'openshift-'
    clean = v.strip().lstrip("v")
    for seg in clean.split("."):
        digits = ""
        for ch in seg:
            if ch.isdigit():
                digits += ch
            else:
                break
        if digits:
            parts.append(int(digits))
        else:
            break
    return tuple(parts)


def check_version_in_range(version: str, min_ver: str | None, max_ver: str | None) -> bool:
    """Check if version is within [min_ver, max_ver] inclusive."""
    v_tuple = parse_version_tuple(version)
    if not v_tuple:
        return True
    # Ensure 3 elements for comparison (major, minor, patch)
    v_padded = (v_tuple + (0, 0))[:3]

    if min_ver:
        min_tuple = parse_version_tuple(min_ver)
        if min_tuple:
            min_padded = (min_tuple + (0, 0))[:3]
            if v_padded < min_padded:
                return False
    if max_ver:
        max_tuple = parse_version_tuple(max_ver)
        if max_tuple:
            # If max is '4.22' (2 parts), allow all patch releases 4.22.x
            max_padded = (max_tuple + (999999, 999999))[:3]
            if v_padded > max_padded:
                return False
    return True


def assess(
    db: Session,
    cluster: Cluster,
    target_version: str,
    live_conditional_updates: list[dict] | None = None,
) -> Assessment:
    """Run deterministic compatibility checks and persist the assessment row."""
    current_version = cluster.ocp_version
    blockers: list[str] = []
    caveats: list[str] = []
    info: list[str] = []

    # 1. Check Upgrade Graph Connectivity
    edges = (
        db.query(UpgradeEdge)
        .filter(
            UpgradeEdge.from_version == current_version,
            UpgradeEdge.to_version == target_version,
        )
        .all()
    )

    if not edges:
        blockers.append(
            f"No direct upgrade path found in Cincinnati graph from {current_version} to {target_version}."
        )
    else:
        info.append(f"Upgrade path from {current_version} to {target_version} exists in Cincinnati graph.")
        # Check graph conditional risks
        conditional_edges = [e for e in edges if e.conditional]
        if conditional_edges:
            for ce in conditional_edges:
                risk_desc = ce.risk_name or "Unspecified conditional risk"
                msg = f"Graph flags conditional risk: {risk_desc}"
                if ce.risk_message:
                    msg += f" - {ce.risk_message}"
                caveats.append(msg)

    # 2. Check Live Cluster Conditional Updates (if provided)
    if live_conditional_updates:
        matching_live_risks = [
            u for u in live_conditional_updates if u.get("version") == target_version
        ]
        for item in matching_live_risks:
            for risk in item.get("risks", []):
                risk_name = risk.get("name", "UnknownRisk")
                risk_msg = risk.get("message", "")
                caveats.append(f"Active cluster conditional risk on target {target_version}: {risk_name} ({risk_msg})")

    # 3. Check Installed Operator Compatibility (Dell CSM, Portworx, OCV, etc.)
    installed_components = (
        db.query(ComponentVersion)
        .filter(ComponentVersion.cluster_id == cluster.id)
        .all()
    )

    for comp in installed_components:
        if comp.component == "ocp":
            continue
        compat_rules = (
            db.query(OperatorCompat)
            .filter(
                OperatorCompat.component == comp.component,
                OperatorCompat.operator_version == comp.version,
            )
            .all()
        )
        if compat_rules:
            is_compat = any(
                check_version_in_range(target_version, r.min_ocp, r.max_ocp)
                for r in compat_rules
            )
            if not is_compat:
                rule = compat_rules[0]
                blockers.append(
                    f"Operator '{comp.component}' version {comp.version} is incompatible with target OCP {target_version} "
                    f"(supported range: {rule.min_ocp or 'any'} to {rule.max_ocp or 'any'})."
                )
            else:
                info.append(f"Operator '{comp.component}' version {comp.version} verified compatible with {target_version}.")

    # 4. Check Red Hat Product Lifecycle (GA, Support, EOL)
    target_major_minor = ".".join(target_version.split(".")[:2])
    lifecycle = (
        db.query(ProductLifecycle)
        .filter(
            ProductLifecycle.component == "ocp",
            ProductLifecycle.version.like(f"%{target_major_minor}%"),
        )
        .first()
    )

    if lifecycle:
        today = dt.date.today()
        if lifecycle.eol_date and today >= lifecycle.eol_date:
            blockers.append(f"Target version {target_version} reached End of Life (EOL) on {lifecycle.eol_date}.")
        elif lifecycle.maintenance_end and today >= lifecycle.maintenance_end:
            caveats.append(f"Target version {target_version} is past maintenance support (ended {lifecycle.maintenance_end}).")
        else:
            info.append(f"Target version {target_version} is within active support window.")

    # Determine Verdict
    if blockers:
        verdict = "no-go"
    elif caveats:
        verdict = "go-with-caveats"
    else:
        verdict = "go"

    reasons: dict[str, Any] = {
        "verdict": verdict,
        "current_version": current_version,
        "target_version": target_version,
        "blockers": blockers,
        "caveats": caveats,
        "info": info,
    }

    assessment = Assessment(
        cluster_id=cluster.id,
        target_version=target_version,
        verdict=verdict,
        reasons=reasons,
        evaluated_at=dt.datetime.now(dt.timezone.utc),
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment
```

---

### `engine/llm_advisor.py`

```python
"""Strategic Upgrade & Migration LLM Advisor Engine.

Provides unified JSON output across both:
  - Deterministic evaluation mode (fast rule-based checks)
  - LLM evaluation mode (deep reasoning + TestOps risk synthesis via local/remote LLM)

Both modes output the exact same JSON schema.
"""
from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

from db.models import Assessment, Cluster, ComponentVersion, OperatorCompat, ProductLifecycle, UpgradeEdge
from engine.compatibility import check_version_in_range, parse_version_tuple

log = logging.getLogger(__name__)

DEFAULT_LLM_URL = "http://127.0.0.1:8080/v1/chat/completions"


def query_local_llm(
    prompt: str,
    system_prompt: str | None = None,
    llm_url: str | None = None,
    model_name: str | None = None,
    timeout: int = 90,
) -> str | None:
    """Query OpenAI-compatible local LLM endpoint (e.g. llama.cpp / vLLM on localhost:8080)."""
    import requests

    url = llm_url or os.environ.get("LLM_URL", DEFAULT_LLM_URL)
    default_system = (
        "You are a Senior OpenShift Platform SRE and Virtualization Upgrade Specialist. "
        "Analyze the provided cluster facts, operator matrix (MTV, Dell CSM, Portworx), "
        "and TestOps policies. Always output valid JSON matching the requested schema."
    )
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt or default_system},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 600,
        "temperature": 0.1,
    }
    if model_name:
        payload["model"] = model_name

    try:
        resp = requests.post(url, json=payload, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "").strip()
    except Exception as exc:
        log.warning("Local LLM request to %s failed: %s (using expert rule engine)", url, exc)
    return None


def fetch_confluence_policy(
    confluence_base_url: str | None = None,
    page_id: str | None = None,
    auth_token: str | None = None,
) -> str | None:
    """Placeholder for future direct Confluence REST API ingestion."""
    base_url = confluence_base_url or os.environ.get("CONFLUENCE_URL")
    pid = page_id or os.environ.get("CONFLUENCE_PAGE_ID")
    token = auth_token or os.environ.get("CONFLUENCE_API_TOKEN")

    if not base_url or not pid:
        return None

    import requests

    try:
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        resp = requests.get(f"{base_url.rstrip('/')}/wiki/rest/api/content/{pid}?expand=body.storage", headers=headers, timeout=15)
        if resp.status_code == 200:
            return resp.json().get("body", {}).get("storage", {}).get("value", "")
    except Exception as exc:
        log.warning("Confluence API fetch failed: %s (using default policy)", exc)
    return None


def load_testops_policy(file_path: str | None = None) -> str:
    """Load TestOps policy (from Confluence API placeholder, custom file, or built-in defaults)."""
    confluence_content = fetch_confluence_policy()
    if confluence_content:
        return confluence_content

    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except OSError:
            pass

    default_path = os.path.join(os.getcwd(), "data", "testops_confluence_policy.md")
    if os.path.exists(default_path):
        try:
            with open(default_path, "r", encoding="utf-8") as f:
                return f.read()
        except OSError:
            pass

    return "TestOps Policy Standard: Prioritize active VM migration (MTV) continuity. Require CSI storage failover verification."


def calculate_version_drift(current_version: str, target_version: str) -> dict[str, Any]:
    """Calculate major, minor, and patch drift."""
    cur_parts = parse_version_tuple(current_version)
    tgt_parts = parse_version_tuple(target_version)

    major_cur = cur_parts[0] if len(cur_parts) > 0 else 4
    major_tgt = tgt_parts[0] if len(tgt_parts) > 0 else 4
    minor_cur = cur_parts[1] if len(cur_parts) > 1 else 0
    minor_tgt = tgt_parts[1] if len(tgt_parts) > 1 else 0
    patch_cur = cur_parts[2] if len(cur_parts) > 2 else 0
    patch_tgt = tgt_parts[2] if len(tgt_parts) > 2 else 0

    is_major_drift = major_tgt > major_cur
    is_downgrade = (tgt_parts + (0, 0, 0))[:3] < (cur_parts + (0, 0, 0))[:3]
    minor_diff = (major_tgt * 100 + minor_tgt) - (major_cur * 100 + minor_cur)
    is_multi_minor_jump = minor_diff > 1

    drift_type = "major" if is_major_drift else (
        "downgrade" if is_downgrade else (
            "multi-minor" if is_multi_minor_jump else (
                "minor" if minor_diff == 1 else "z-stream"
            )
        )
    )

    return {
        "current": current_version,
        "target": target_version,
        "is_major_drift": is_major_drift,
        "is_downgrade": is_downgrade,
        "is_multi_minor_jump": is_multi_minor_jump,
        "drift_type": drift_type,
        "minor_steps": minor_diff,
    }


def extract_json_payload(raw_text: str) -> dict[str, Any] | None:
    """Attempt to parse JSON from LLM output, extracting from markdown fences if needed."""
    if not raw_text:
        return None
    clean = raw_text.strip()
    # Check for markdown code fence
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", clean, re.DOTALL)
    if fence_match:
        try:
            return json.loads(fence_match.group(1))
        except json.JSONDecodeError:
            pass
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        return None


def generate_expert_decision(
    cluster: Cluster,
    target_version: str,
    assessment: Assessment,
    installed_components: list[ComponentVersion],
    compat_records: list[OperatorCompat],
    cve_count: int,
    critical_cve_count: int,
    policy_text: str,
) -> dict[str, Any]:
    """Fallback deterministic logic mimicking the LLM's comprehensive decision framework."""
    drift = calculate_version_drift(cluster.ocp_version, target_version)
    reasons_data = assessment.reasons or {}
    deterministic_verdict = assessment.verdict.upper()

    verdict = deterministic_verdict
    escalation_reasons: list[str] = list(reasons_data.get("blockers") or [])

    if drift["is_downgrade"]:
        verdict = "NO-GO (ESCALATE)"
        escalation_reasons.append(
            f"In-place platform downgrade/rollback ({cluster.ocp_version} -> {target_version}) is strictly unsupported "
            "by OpenShift Container Platform, Kubernetes, and CVO/MCO architecture. Rollbacks require full cluster redeployment or etcd disaster recovery restore."
        )

    if drift["is_major_drift"]:
        verdict = "NO-GO (ESCALATE)"
        escalation_reasons.append(
            f"Major version architectural drift detected ({cluster.ocp_version} -> {target_version}). "
            "Under TestOps Policy, major version transitions require mandatory sandbox qualification."
        )

    components_map = {c.component: c.version for c in installed_components}
    operator_risks = []

    for comp, ver in components_map.items():
        if comp == "ocp":
            continue
        rules = [r for r in compat_records if r.component == comp and r.operator_version == ver]
        if rules:
            if not any(check_version_in_range(target_version, r.min_ocp, r.max_ocp) for r in rules):
                max_supported = rules[0].max_ocp or "any"
                operator_risks.append(
                    f"{comp} (version {ver}) is NOT certified for OCP {target_version} (supported up to {max_supported})."
                )
        elif drift["is_major_drift"]:
            operator_risks.append(
                f"{comp} (version {ver}) has no verified compatibility rule for major release {target_version}."
            )

    # Re-use core generation logic for the output structure
    return generate_strategic_analysis(
        cluster, target_version, assessment, installed_components, compat_records, 
        cve_count, critical_cve_count, policy_text
    )


def generate_strategic_analysis(
    cluster: Cluster,
    target_version: str,
    assessment: Assessment,
    installed_components: list[ComponentVersion],
    compat_records: list[OperatorCompat],
    cve_count: int,
    critical_cve_count: int,
    policy_text: str,
    llm_url: str | None = None,
    use_live_llm: bool = False,
) -> dict[str, Any]:
    """Generate unified JSON strategic assessment across deterministic and LLM modes."""
    drift = calculate_version_drift(cluster.ocp_version, target_version)
    components_map = {c.component: c.version for c in installed_components}

    # Evaluate critical operator risks
    operator_risks: list[str] = []
    for comp in installed_components:
        comp_rules = [r for r in compat_records if r.component == comp.component and r.operator_version == comp.version]
        if comp_rules:
            is_compat = any(check_version_in_range(target_version, r.min_ocp, r.max_ocp) for r in comp_rules)
            if not is_compat:
                rule = comp_rules[0]
                operator_risks.append(
                    f"{comp.component} (version {comp.version}) is NOT certified for OCP {target_version} "
                    f"(supported up to {rule.max_ocp or 'current'})."
                )

    # Core Rule Reasoning
    escalation_reasons: list[str] = []
    verdict = assessment.verdict.upper()

    if drift["is_downgrade"]:
        verdict = "NO-GO (ESCALATE)"
        escalation_reasons.append(
            f"In-place platform downgrade/rollback ({cluster.ocp_version} -> {target_version}) is strictly unsupported "
            "by OpenShift Container Platform, Kubernetes, and CVO/MCO architecture. Rollbacks require full cluster redeployment or etcd disaster recovery restore."
        )

    if drift["is_major_drift"]:
        verdict = "NO-GO (ESCALATE)"
        escalation_reasons.append(
            f"Major version architectural drift detected ({cluster.ocp_version} -> {target_version}). "
            "Under TestOps Policy, major version transitions require mandatory sandbox qualification."
        )

    if operator_risks:
        verdict = "NO-GO (ESCALATE)"
        escalation_reasons.extend(operator_risks)

    if "mtv" in components_map:
        mtv_ver = components_map["mtv"]
        if drift["is_major_drift"] or drift["is_multi_minor_jump"]:
            escalation_reasons.append(
                f"Active MTV (Migration Toolkit for Virtualization) operator v{mtv_ver} detected. "
                "VM migration stability is prioritized over routine platform upgrades unless critical CVEs are unpatched."
            )

    # Build Executive Synopsis
    if "ESCALATE" in verdict or verdict == "NO-GO":
        synopsis = (
            f"RECOMMENDATION: HOLD UPGRADE (NO-GO ESCALATED). Upgrading cluster '{cluster.name}' from "
            f"OCP {cluster.ocp_version} to {target_version} poses high operational risk to active migration and storage workloads. "
            f"Identified {len(escalation_reasons)} primary blocker(s) including version drift and operator boundary mismatches. "
            "Platform SRE and TestOps sign-off is strictly required prior to staging validation."
        )
    elif verdict == "GO-WITH-CAVEATS":
        synopsis = (
            f"RECOMMENDATION: PROCEED WITH TARGETED CAVEATS. Upgrading cluster '{cluster.name}' from "
            f"OCP {cluster.ocp_version} to {target_version} is architecturally supported, but conditional update risks "
            "or storage driver advisories require pre-upgrade staging verification."
        )
    else:
        synopsis = (
            f"RECOMMENDATION: APPROVED FOR STAGED ROLLOUT (GO). Target release {target_version} provides verified "
            f"compatibility across MTV, Dell CSM, and Portworx without major version drift."
        )

    # Build Dynamic Impact Breakdown from DB records
    storage_comps = [c.component for c in installed_components if any(kw in c.component.lower() for kw in ["csm", "csi", "storage", "portworx", "odf", "ceph"])]
    migration_comps = [c.component for c in installed_components if any(kw in c.component.lower() for kw in ["mtv", "forklift", "migration", "v2v"])]

    dynamic_impact: dict[str, Any] = {
        "migration_impact": (
            f"HIGH RISK: Detected migration operator(s) ({', '.join(migration_comps)}). Major version drift or uncertified target may disrupt active VM cutovers and disk transfer streams."
            if migration_comps and (drift["is_major_drift"] or operator_risks)
            else (f"STABLE: Migration operator(s) ({', '.join(migration_comps)}) verified within certified range." if migration_comps else "N/A: No active VM migration operators installed.")
        ),
        "storage_impact": (
            f"CRITICAL RISK: Storage CSI operator(s) ({', '.join(storage_comps)}) require kernel header validation and CSI node-driver re-certification on target Kubernetes base."
            if storage_comps and (operator_risks or drift["is_major_drift"])
            else (f"VERIFIED: Storage operator(s) ({', '.join(storage_comps)}) certified for target version." if storage_comps else "N/A: No custom CSI storage operators installed.")
        ),
        "security_delta": f"{critical_cve_count} Critical and {cve_count} Important CVE/RHSAs tracked in database.",
        "version_drift": drift,
    }

    # Build Dynamic Staging Remediation Plan based on installed DB inventory
    testops_plan = []
    step_num = 1
    if operator_risks:
        testops_plan.append({
            "step": step_num,
            "phase": "Pre-Requisite Operator Upgrades",
            "action": f"Upgrade uncertified operator(s) ({', '.join([c.component for c in installed_components])}) to versions supporting OCP {target_version}.",
            "gate": "Operator CSVs reach Succeeded phase with 0 CrashLoopBackOff pods.",
        })
        step_num += 1

    if migration_comps:
        testops_plan.append({
            "step": step_num,
            "phase": "Sandbox Live Migration Test",
            "action": f"Execute end-to-end VM warm migration dry run using {', '.join(migration_comps)} on target OCP build.",
            "gate": "Zero data corruption, successful cutover under SLA window.",
        })
        step_num += 1

    if storage_comps:
        testops_plan.append({
            "step": step_num,
            "phase": "CSI Storage Failover Verification",
            "action": f"Trigger worker node drain and reboot under I/O load on storage operators ({', '.join(storage_comps)}).",
            "gate": "Volumes reattach within 30s without VolumeAttachment timeout.",
        })
        step_num += 1

    testops_plan.append({
        "step": step_num,
        "phase": "Fleet Canary Deployment",
        "action": "Roll out upgrade to 1 non-prod lab cluster before scheduling production fleet windows.",
        "gate": "ClusterVersion reaches Available=True with 0 cluster operator degraded alerts for 48 hours.",
    })

    # Dynamic Human Sign-off Form
    checklist = ["[ ] Maintenance window approved by Change Advisory Board (CAB)"]
    if migration_comps:
        checklist.insert(0, f"[ ] All active VM migrations on {', '.join(migration_comps)} paused / drained")
    if storage_comps:
        checklist.insert(1, f"[ ] Sandbox failover test passed on {', '.join(storage_comps)}")
    if operator_risks or drift["is_major_drift"]:
        checklist.insert(2, "[ ] TestOps qualification test suite executed on target build in staging")

    human_sign_off = {
        "status": "PENDING_APPROVAL" if "NO-GO" in verdict or "CAVEATS" in verdict else "AUTO_APPROVED",
        "required_approvers": ["TestOps Lead", "Cloud Platform SRE Lead", "Storage Administrator"],
        "sign_off_checklist": checklist,
    }

    # Base unified structure
    unified_result: dict[str, Any] = {
        "cluster": cluster.name,
        "current_version": cluster.ocp_version,
        "target_version": target_version,
        "evaluation_mode": "llm" if use_live_llm else "deterministic",
        "verdict": verdict,
        "executive_synopsis": synopsis,
        "reasons": {
            "blockers": assessment.reasons.get("blockers", []) + escalation_reasons,
            "caveats": assessment.reasons.get("caveats", []),
            "info": assessment.reasons.get("info", []),
        },
        "impact_analysis": dynamic_impact,
        "testops_remediation_plan": testops_plan,
        "human_in_the_loop_sign_off": human_sign_off,
        "evaluated_at": assessment.evaluated_at.isoformat() if assessment.evaluated_at else None,
    }

    # If LLM mode is active, prompt the LLM to think and return the JSON decision
    if use_live_llm:
        system_prompt = (
            "You are an expert SRE and OpenShift Virtualization Upgrade Decision Engine. "
            "You evaluate cluster upgrade safety against TestOps policies and return a JSON decision. "
            "Return ONLY valid JSON matching this schema:\n"
            "{\n"
            '  "verdict": "GO" | "GO-WITH-CAVEATS" | "NO-GO" | "NO-GO (ESCALATE)",\n'
            '  "executive_synopsis": "string",\n'
            '  "reasons": {"blockers": ["string"], "caveats": ["string"], "info": ["string"]},\n'
            '  "impact_analysis": {"migration_impact": "string", "storage_impact": "string", "security_delta": "string"}\n'
            "}"
        )
        llm_prompt = (
            f"Cluster: {cluster.name}\n"
            f"Current OCP Version: {cluster.ocp_version}\n"
            f"Target OCP Version: {target_version}\n"
            f"Installed Operators: {json.dumps(components_map)}\n"
            f"Version Drift: {drift['drift_type']} (Major Drift: {drift['is_major_drift']})\n"
            f"Deterministic Check: {assessment.verdict.upper()}\n"
            f"Identified Risks: {json.dumps(escalation_reasons)}\n"
            f"TestOps Policy: Prioritize active VM migration continuity. Require CSI storage validation.\n\n"
            "Analyze the upgrade and return your JSON decision."
        )
        raw_llm_out = query_local_llm(llm_prompt, system_prompt=system_prompt, llm_url=llm_url)
        parsed_llm = extract_json_payload(raw_llm_out) if raw_llm_out else None

        if parsed_llm and "verdict" in parsed_llm:
            unified_result["verdict"] = str(parsed_llm.get("verdict", verdict)).upper()
            if "executive_synopsis" in parsed_llm:
                unified_result["executive_synopsis"] = parsed_llm["executive_synopsis"]
            if "reasons" in parsed_llm and isinstance(parsed_llm["reasons"], dict):
                unified_result["reasons"].update(parsed_llm["reasons"])
            if "impact_analysis" in parsed_llm and isinstance(parsed_llm["impact_analysis"], dict):
                unified_result["impact_analysis"].update(parsed_llm["impact_analysis"])
            unified_result["evaluation_mode"] = "llm"
        elif raw_llm_out:
            # LLM returned text rather than strict JSON; use LLM narrative as synopsis
            unified_result["executive_synopsis"] = f"[LLM Decision] {raw_llm_out}"
            unified_result["evaluation_mode"] = "llm"

    return unified_result
```

---

### `gitops/__init__.py`

```python
"""GitOps automation bot for OpenShift / OCV fleet upgrades."""
from __future__ import annotations

from gitops.bot import RepoTarget, open_or_update_pr

__all__ = ["RepoTarget", "open_or_update_pr"]
```

---

### `gitops/bot.py`

```python
"""GitOps pull request bot for OpenShift / OCV cluster upgrades.

Automates the lifecycle of GitOps PRs that bump a cluster's target OCP version:
  1. Validates gated assessment status (refusing NO-GO).
  2. Modifies cluster manifests (e.g. ACM ClusterCurator / ClusterDeployment CRs)
     using ruamel.yaml to preserve formatting, comments, and structure.
  3. Manages git branches, commits, and pushes via GitPython.
  4. Interacts with GitHub REST API to open new PRs (marking caveats as draft by default)
     or updating existing branches/PRs idempotently.
"""
from __future__ import annotations

import dataclasses
import logging
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, urlunparse

import git
import requests
from ruamel.yaml import YAML

log = logging.getLogger(__name__)


@dataclass
class RepoTarget:
    """GitOps repository configuration for a target cluster."""

    repo_url: str
    owner: str
    repo_name: str
    cluster_path: str
    curator_namespace: str
    base_branch: str = "main"
    upstream_graph_url: str | None = None


def get_authenticated_repo_url(repo_url: str, token: str) -> str:
    """Inject personal access token or installation token into HTTPS clone URL."""
    if not token or not repo_url.startswith("https://"):
        return repo_url
    parsed = urlparse(repo_url)
    auth_netloc = f"x-access-token:{token}@{parsed.netloc}"
    return urlunparse(parsed._replace(netloc=auth_netloc))


def create_yaml_parser() -> YAML:
    """Create a round-trip YAML parser preserving comments and indentation."""
    y = YAML()
    y.preserve_quotes = True
    y.indent(mapping=2, sequence=4, offset=2)
    return y


def update_cluster_manifests(
    repo_root: Path,
    target: RepoTarget,
    cluster_name: str,
    target_version: str,
) -> list[str]:
    """Find and update cluster upgrade manifests (e.g. ClusterCurator) using ruamel.yaml.

    Returns a list of updated file paths relative to repo_root.
    """
    cluster_dir = repo_root / target.cluster_path
    cluster_dir.mkdir(parents=True, exist_ok=True)
    yaml_parser = create_yaml_parser()
    modified_files: list[str] = []

    # Look for candidate YAML files in the cluster directory
    candidate_files = list(cluster_dir.glob("*.yaml")) + list(cluster_dir.glob("*.yml"))
    curator_found = False

    target_major_minor = ".".join(target_version.split(".")[:2])

    for fpath in candidate_files:
        try:
            with open(fpath, "r", encoding="utf-8") as fh:
                doc = yaml_parser.load(fh)
        except Exception as exc:
            log.warning("Could not parse %s as YAML: %s", fpath, exc)
            continue

        if not isinstance(doc, dict):
            continue

        kind = doc.get("kind")
        if kind == "ClusterCurator":
            curator_found = True
            spec = doc.setdefault("spec", {})
            spec["desiredCuration"] = "upgrade"
            upgrade_spec = spec.setdefault("upgrade", {})
            upgrade_spec["desiredUpdate"] = target_version
            if target.upstream_graph_url:
                upgrade_spec["upstream"] = target.upstream_graph_url
            if "channel" in upgrade_spec:
                upgrade_spec["channel"] = f"stable-{target_major_minor}"

            with open(fpath, "w", encoding="utf-8") as fh:
                yaml_parser.dump(doc, fh)
            modified_files.append(str(fpath.relative_to(repo_root)).replace("\\", "/"))
            log.info("Updated ClusterCurator in %s to target %s", fpath, target_version)

        elif kind in ("ClusterDeployment", "ClusterVersion"):
            spec = doc.setdefault("spec", {})
            if "desiredUpdate" in spec and isinstance(spec["desiredUpdate"], dict):
                spec["desiredUpdate"]["version"] = target_version
                with open(fpath, "w", encoding="utf-8") as fh:
                    yaml_parser.dump(doc, fh)
                modified_files.append(str(fpath.relative_to(repo_root)).replace("\\", "/"))
                log.info("Updated %s in %s to version %s", kind, fpath, target_version)

    # If no curator manifest existed, synthesize standard ACM ClusterCurator CR
    if not curator_found and not modified_files:
        curator_file = cluster_dir / "cluster-curator.yaml"
        curator_manifest = {
            "apiVersion": "cluster.open-cluster-management.io/v1beta1",
            "kind": "ClusterCurator",
            "metadata": {
                "name": cluster_name,
                "namespace": target.curator_namespace,
                "labels": {
                    "open-cluster-management.io/cluster-name": cluster_name,
                },
            },
            "spec": {
                "desiredCuration": "upgrade",
                "upgrade": {
                    "channel": f"stable-{target_major_minor}",
                    "desiredUpdate": target_version,
                },
            },
        }
        if target.upstream_graph_url:
            curator_manifest["spec"]["upgrade"]["upstream"] = target.upstream_graph_url

        with open(curator_file, "w", encoding="utf-8") as fh:
            yaml_parser.dump(curator_manifest, fh)
        modified_files.append(str(curator_file.relative_to(repo_root)).replace("\\", "/"))
        log.info("Created new ClusterCurator manifest at %s", curator_file)

    return modified_files


def render_pr_body(
    cluster_name: str,
    current_version: str,
    target_version: str,
    verdict: str,
    reasons: dict[str, Any],
    assessment_id: int | str,
    evaluated_at: str,
) -> str:
    """Generate structured, audit-ready Markdown PR description."""
    verdict_badge = "**GO** :white_check_mark:" if verdict == "go" else "**GO WITH CAVEATS** :warning:"
    if verdict == "no-go":
        verdict_badge = "**NO-GO** :x:"

    blockers = reasons.get("blockers") or reasons.get("blocking") or []
    caveats = reasons.get("caveats") or []
    info = reasons.get("info") or []

    lines = [
        f"## :robot: Automated Pre-Upgrade Assessment — {cluster_name}",
        "",
        f"This Pull Request proposes bumping cluster **`{cluster_name}`** OCP target from **`{current_version}`** to **`{target_version}`**.",
        "",
        f"| Parameter | Value |",
        f"| :--- | :--- |",
        f"| **Cluster** | `{cluster_name}` |",
        f"| **Current Version** | `{current_version}` |",
        f"| **Target Version** | `{target_version}` |",
        f"| **Assessment Verdict** | {verdict_badge} |",
        f"| **Assessment ID** | `#{assessment_id}` |",
        f"| **Evaluated At** | `{evaluated_at}` |",
        "",
    ]

    if verdict == "go-with-caveats":
        lines.extend([
            "> [!WARNING]",
            "> **This upgrade has conditional risks or caveats.**",
            "> This PR was created in draft mode for engineering review.",
            "",
        ])

    if caveats:
        lines.extend([
            "### :warning: Caveats & Conditional Risks",
            "",
        ])
        for c in caveats:
            detail = c.get("detail", c) if isinstance(c, dict) else c
            kind = c.get("kind") if isinstance(c, dict) else None
            prefix = f"**[{kind}]** " if kind else ""
            lines.append(f"- {prefix}{detail}")
        lines.append("")

    if blockers:
        lines.extend([
            "### :no_entry_sign: Blocking Issues",
            "",
        ])
        for b in blockers:
            detail = b.get("detail", b) if isinstance(b, dict) else b
            kind = b.get("kind") if isinstance(b, dict) else None
            prefix = f"**[{kind}]** " if kind else ""
            lines.append(f"- {prefix}{detail}")
        lines.append("")

    if info:
        lines.extend([
            "### :white_check_mark: Validated Compatibility Checks",
            "",
        ])
        for item in info:
            lines.append(f"- {item}")
        lines.append("")

    lines.extend([
        "### :clipboard: Pre-Merge Checklist",
        "- [ ] Verify disconnected/air-gapped release payload mirroring if applicable",
        "- [ ] Ensure active VM migrations (MTV) are quiescent before initiating node drains",
        "- [ ] Validate CSI storage replication & backup health (Dell CSM / Portworx)",
        "- [ ] Confirm maintenance window approval with TestOps / Release Engineering",
        "",
        "---",
        "*Automated by [OCV Upgrade & Migration Assessment Agent](https://github.com/openshift-virtualization/ocv-upgrade-agent)*",
    ])

    return "\n".join(lines)


def open_or_update_pr(
    cluster_name: str,
    current_version: str,
    target_version: str,
    verdict: str,
    reasons: dict[str, Any],
    target: RepoTarget,
    token: str,
    assessment_id: int | str,
    evaluated_at: str,
    force_ready: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Create or update a GitOps PR for a cluster upgrade."""
    branch_name = f"upgrade/{cluster_name}-to-{target_version}"
    commit_msg = f"feat(gitops): bump {cluster_name} OCP target to {target_version}"
    pr_title = f"feat(gitops): upgrade {cluster_name} to OCP {target_version} [{verdict.upper()}]"
    is_draft = (verdict == "go-with-caveats") and not force_ready

    pr_body = render_pr_body(
        cluster_name=cluster_name,
        current_version=current_version,
        target_version=target_version,
        verdict=verdict,
        reasons=reasons,
        assessment_id=assessment_id,
        evaluated_at=evaluated_at,
    )

    with tempfile.TemporaryDirectory(prefix="gitops_bot_", ignore_cleanup_errors=True) as temp_dir:
        repo_dir = Path(temp_dir) / "repo"
        repo = None

        try:
            if dry_run:
                log.info("[DRY-RUN] Simulating GitOps PR creation for %s -> %s", cluster_name, target_version)
                repo = git.Repo.init(repo_dir)
                # Create base branch and initial commit
                base_file = repo_dir / "README.md"
                base_file.write_text(f"# Fleet GitOps for {target.owner}/{target.repo_name}\n", encoding="utf-8")
                repo.index.add(["README.md"])
                repo.index.commit("initial commit")
                repo.create_head(target.base_branch)
                repo.git.checkout(target.base_branch)

                # Create branch
                head_branch = repo.create_head(branch_name)
                head_branch.checkout()

                modified_files = update_cluster_manifests(repo_dir, target, cluster_name, target_version)
                repo.index.add(modified_files)
                diff_text = repo.git.diff("HEAD")

                return {
                    "action": "dry-run-preview",
                    "cluster": cluster_name,
                    "current_version": current_version,
                    "target_version": target_version,
                    "verdict": verdict,
                    "branch": branch_name,
                    "base_branch": target.base_branch,
                    "draft": is_draft,
                    "pr_title": pr_title,
                    "pr_body": pr_body,
                    "modified_files": modified_files,
                    "diff": diff_text,
                }

            # Live Execution: Clone repo with auth
            auth_url = get_authenticated_repo_url(target.repo_url, token)
            log.info("Cloning GitOps repo %s...", target.repo_url)
            repo = git.Repo.clone_from(auth_url, repo_dir, branch=target.base_branch)

            # Checkout or create upgrade branch
            try:
                repo.git.checkout(branch_name)
                log.info("Checked out existing branch %s", branch_name)
            except git.GitCommandError:
                repo.git.checkout("-b", branch_name)
                log.info("Created and checked out new branch %s", branch_name)

            modified_files = update_cluster_manifests(repo_dir, target, cluster_name, target_version)

            if not modified_files:
                log.warning("No files modified during manifest update")

            # Commit and push
            repo.git.add(A=True)
            if repo.is_dirty(untracked_files=True):
                repo.index.commit(commit_msg)
                log.info("Committed changes: %s", commit_msg)
            else:
                log.info("Working directory clean; no new commit needed")

            log.info("Pushing branch %s to remote...", branch_name)
            origin = repo.remote(name="origin")
            origin.push(refspec=f"{branch_name}:{branch_name}", set_upstream=True, force=True)

            # GitHub API: Check for existing PR
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
            api_base = "https://api.github.com"
            pulls_url = f"{api_base}/repos/{target.owner}/{target.repo_name}/pulls"

            list_resp = requests.get(
                pulls_url,
                headers=headers,
                params={"head": f"{target.owner}:{branch_name}", "state": "open", "base": target.base_branch},
                timeout=30,
            )
            list_resp.raise_for_status()
            existing_prs = list_resp.json()

            if existing_prs:
                pr = existing_prs[0]
                pr_number = pr["number"]
                pr_url = pr["html_url"]
                log.info("Found existing open PR #%d: %s; updating...", pr_number, pr_url)

                update_resp = requests.patch(
                    f"{pulls_url}/{pr_number}",
                    headers=headers,
                    json={"title": pr_title, "body": pr_body, "draft": is_draft},
                    timeout=30,
                )
                update_resp.raise_for_status()
                action = "updated"
            else:
                log.info("Opening new PR for %s...", branch_name)
                create_resp = requests.post(
                    pulls_url,
                    headers=headers,
                    json={
                        "title": pr_title,
                        "body": pr_body,
                        "head": branch_name,
                        "base": target.base_branch,
                        "draft": is_draft,
                    },
                    timeout=30,
                )
                create_resp.raise_for_status()
                pr_data = create_resp.json()
                pr_url = pr_data["html_url"]
                pr_number = pr_data["number"]
                action = "created"

            return {
                "action": action,
                "pr_url": pr_url,
                "pr_number": pr_number,
                "cluster": cluster_name,
                "target_version": target_version,
                "branch": branch_name,
                "draft": is_draft,
                "modified_files": modified_files,
            }
        finally:
            if repo is not None:
                try:
                    repo.close()
                except Exception:
                    pass
```

---

### `requirements.txt`

```text
SQLAlchemy>=2.0,<3.0
requests>=2.31
PyYAML>=6.0
ruamel.yaml>=0.18       # round-trip-safe YAML editing for the GitOps PR bot
kubernetes>=29.0
GitPython>=3.1
psycopg2-binary>=2.9    # only needed where DATABASE_URL points at Postgres
pytest>=8.0
```

---

### `run_assessment.py`

```python
#!/usr/bin/env python3
"""Run an automated upgrade assessment for one cluster x candidate target version.

Unified Assessment Engine:
  - Default: Deterministic evaluation (fast, 100% rule-based facts check)
  - With --llm: LLM-driven decision & reasoning (via local/remote LLM endpoint)

Both modes output the exact same JSON decision schema.

Examples:
    # 1. Deterministic Mode (Default):
    python run_assessment.py --cluster east-prod-01 --target 4.22.8

    # 2. LLM Mode (Local LLM thinking):
    python run_assessment.py --cluster east-prod-01 --target 4.22.8 --llm

    # 3. Pure JSON Output (for CI/CD pipelines & GitOps bots):
    python run_assessment.py --cluster east-prod-01 --target 4.22.8 --json
"""
from __future__ import annotations

import argparse
import json
import logging

log = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(
        description="Run an automated GO / GO-WITH-CAVEATS / NO-GO upgrade compatibility assessment."
    )
    ap.add_argument("--cluster", required=True, help="cluster name from inventory (e.g. east-prod-01)")
    ap.add_argument("--target", required=True, help="candidate target OCP version (e.g. 4.22.8 or 5.0.0)")
    ap.add_argument("--llm", action="store_true", help="use LLM for decision reasoning and analysis (default: deterministic)")
    ap.add_argument("--llm-url", default="http://127.0.0.1:8080/v1/chat/completions", help="local or remote LLM endpoint URL")
    ap.add_argument("--json", action="store_true", help="output strictly raw JSON (ideal for GitOps bots & scripts)")
    ap.add_argument("--confluence-page-id", help="placeholder: Confluence Page ID for API ingestion")
    ap.add_argument("--confluence-url", help="placeholder: Confluence Base URL")
    ap.add_argument("--kubeconfig", help="path to kubeconfig for live ClusterVersion inspection")
    ap.add_argument("--db-url", help="overrides DATABASE_URL")
    args = ap.parse_args()

    from db.db import get_session, init_db
    from db.models import Advisory, Cluster, ComponentVersion, OperatorCompat
    from engine.compatibility import assess
    from engine.llm_advisor import generate_strategic_analysis, load_testops_policy

    init_db(args.db_url)

    with get_session() as db:
        cluster = db.query(Cluster).filter_by(name=args.cluster).one_or_none()
        if cluster is None:
            raise SystemExit(
                f"Cluster {args.cluster!r} not found in inventory. "
                "Add it to the 'clusters' table first or run collectors.cluster_state."
            )

        live_conditional_updates = None
        if args.kubeconfig or cluster.kubeconfig_context:
            try:
                from collectors.cluster_state import fetch_clusterversion, load_api_clients, parse_clusterversion

                api = load_api_clients(context=cluster.kubeconfig_context, kubeconfig_path=args.kubeconfig)
                live = parse_clusterversion(fetch_clusterversion(api))
                live_conditional_updates = live["conditional_updates"]
                log.info("Live ClusterVersion read OK (%d conditional risks reported)", len(live_conditional_updates))
            except Exception as exc:  # noqa: BLE001 - degrade gracefully, don't abort
                log.warning("Live read failed (%s); falling back to database graph risk data", exc)

        row = assess(db, cluster, args.target, live_conditional_updates=live_conditional_updates)

        installed = (
            db.query(ComponentVersion)
            .filter(ComponentVersion.cluster_id == cluster.id)
            .all()
        )
        compat_records = db.query(OperatorCompat).all()
        cve_count = db.query(Advisory).filter(Advisory.severity == "important").count()
        crit_cve_count = db.query(Advisory).filter(Advisory.severity == "critical").count()
        policy_text = load_testops_policy()

        decision_payload = generate_strategic_analysis(
            cluster=cluster,
            target_version=args.target,
            assessment=row,
            installed_components=installed,
            compat_records=compat_records,
            cve_count=cve_count,
            critical_cve_count=crit_cve_count,
            policy_text=policy_text,
            llm_url=args.llm_url,
            use_live_llm=args.llm,
        )

    if args.json:
        print(json.dumps(decision_payload, indent=2, default=str))
        return

    print("\n" + "=" * 70)
    print(f"UPGRADE ASSESSMENT RESULT: {decision_payload['verdict']} [Mode: {decision_payload['evaluation_mode'].upper()}]")
    print("=" * 70)

    print("\n--- [EXECUTIVE SYNOPSIS] ---")
    print(decision_payload["executive_synopsis"])

    blockers = decision_payload["reasons"].get("blockers", [])
    if blockers:
        print("\n--- [ESCALATION & BLOCKER TRIGGERS] ---")
        for r in blockers:
            print(f" • {r}")

    print("\n--- [DEEP COMPONENT & STORAGE IMPACT] ---")
    for k, v in decision_payload["impact_analysis"].items():
        if k != "version_drift":
            print(f" • {k.replace('_', ' ').upper()}: {v}")

    print("\n--- [TESTOPS REMEDIATION & QUALIFICATION PLAN] ---")
    for step in decision_payload["testops_remediation_plan"]:
        print(f" Step {step['step']} [{step['phase']}]:")
        print(f"   Action: {step['action']}")
        print(f"   Gate:   {step['gate']}")

    print("\n--- [HUMAN-IN-THE-LOOP SIGN-OFF GATE] ---")
    print(f" Status: {decision_payload['human_in_the_loop_sign_off']['status']}")
    print(f" Required Approvers: {', '.join(decision_payload['human_in_the_loop_sign_off']['required_approvers'])}")
    print(" Checklist:")
    for item in decision_payload["human_in_the_loop_sign_off"]["sign_off_checklist"]:
        print(f"   {item}")

    print("\n--- [UNIFIED DECISION JSON PAYLOAD] ---")
    print(json.dumps(decision_payload, indent=2, default=str))


if __name__ == "__main__":
    main()
```

---

### `run_collectors.py`

```python
#!/usr/bin/env python3
"""Entry point for running all (or selected) collectors -- this is what your
CronJob/scheduled Job invokes.

Split by network reachability, matching the bastion / disconnected split in
the architecture: run with --only redhat-security,lifecycle,cincinnati on the
connected bastion, ship the resulting DB (or a pg_dump / row export) across
the air gap, then run --only cluster-state,vendor-matrix,release-info inside
the disconnected network where the clusters and mirrored release payloads
actually are.

Examples:
    python run_collectors.py --only redhat-security,lifecycle,cincinnati
    python run_collectors.py --only cluster-state --cluster east-prod-01
"""
from __future__ import annotations

import argparse
import logging

log = logging.getLogger(__name__)

COLLECTORS = {
    "redhat-security": "collectors.redhat_security",
    "lifecycle": "collectors.lifecycle",
    "cincinnati": "collectors.cincinnati",
    "cincinatti": "collectors.cincinnati",  # alias for common spelling
    "vendor-matrix": "collectors.vendor_matrix",
    "cluster-state": "collectors.cluster_state",
    "release-info": "collectors.release_info",
}


EPILOG = """
examples:
  # Pull only security advisories and product lifecycle dates:
  python run_collectors.py --only redhat-security,lifecycle

  # Filter critical/important security advisories released after a date:
  python run_collectors.py --only redhat-security --severity critical --after 2026-01-01

  # Pull upgrade graph for a specific channel into DB:
  python run_collectors.py --only cincinnati --channel stable-4.22

  # Inspect a specific release payload version via `oc adm release info`:
  python run_collectors.py --only release-info --release-version 4.22.0

  # Run all bastion collectors:
  python run_collectors.py --only redhat-security,lifecycle,cincinnati

  # Run disconnected collectors against a specific cluster and release:
  python run_collectors.py --only cluster-state,vendor-matrix,release-info --cluster east-prod-01 --release-version 4.22.0
"""


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(
        description="Run OCV upgrade agent collectors to populate Postgres / SQLite database.",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument(
        "--only",
        help=f"comma-separated subset of: {', '.join(COLLECTORS)} (default: all)",
    )
    ap.add_argument("--cluster", action="append", help="passed through to cluster-state")
    ap.add_argument("--release-version", action="append", help="target release version(s) for release-info (e.g. 4.22.0)")
    ap.add_argument("--channel", action="append", help="channels for cincinnati (e.g. stable-4.22)")
    ap.add_argument("--product", action="append", help="product(s) for redhat-security (default: OCP + OCV)")
    ap.add_argument("--severity", choices=["low", "moderate", "important", "critical"], help="filter redhat-security by severity")
    ap.add_argument("--after", help="filter redhat-security by published date YYYY-MM-DD")
    ap.add_argument("--db-url", help="overrides $DATABASE_URL for this run")
    args, unknown = ap.parse_known_args()

    from db.db import init_db

    init_db(args.db_url)

    selected = args.only.split(",") if args.only else list(COLLECTORS)
    for name in selected:
        if name not in COLLECTORS:
            log.error("Unknown collector %r, skipping. Valid: %s", name, list(COLLECTORS))
            continue
        module = __import__(COLLECTORS[name], fromlist=["collect"])
        log.info("--- running %s ---", name)
        try:
            if name == "cluster-state":
                n = module.collect(cluster_names=args.cluster)
            elif name == "release-info":
                n = module.collect(versions=args.release_version)
            elif name == "cincinnati":
                n = module.collect(channels=args.channel)
            elif name == "redhat-security":
                n = module.collect(products=args.product, severity=args.severity, after=args.after)
            else:
                n = module.collect()
            log.info("--- %s done: %s ---", name, n)
        except Exception:  # noqa: BLE001 - one bad collector shouldn't stop the rest
            log.exception("collector %s failed", name)


if __name__ == "__main__":
    main()
```

---

### `run_gitops_pr.py`

```python
#!/usr/bin/env python3
"""Open (or update) a GitOps PR bumping a cluster's OCP target version, gated
on the most recent stored assessment for that cluster x target.

    python run_gitops_pr.py --cluster east-prod-01 --target 4.22.8 --dry-run
    python run_gitops_pr.py --cluster east-prod-01 --target 4.22.8

Refuses outright on a no-go verdict -- prints the blocking reasons and exits
nonzero, no git/GitHub calls made. A go-with-caveats verdict opens the PR as
a draft by default; pass --force-ready to open it ready-for-review anyway
(the caveats still show up in the PR body either way). Re-running against an
existing branch/PR updates it in place rather than creating a duplicate.

Reads per-cluster repo config from data/gitops_targets.yaml (override with
--targets-file) and the GitHub token from $GITHUB_TOKEN (not required for
--dry-run, which stops before any git push or GitHub API call).
"""
from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path

import git
import requests
import yaml

from db.db import get_session, init_db
from db.models import Assessment, Cluster
from gitops.bot import RepoTarget, open_or_update_pr

log = logging.getLogger(__name__)

DEFAULT_TARGETS_PATH = Path(__file__).resolve().parent / "data" / "gitops_targets.yaml"
REQUIRED_TARGET_KEYS = ["repo_url", "owner", "repo_name", "cluster_path", "curator_namespace"]


def load_target(cluster_name: str, path: Path = DEFAULT_TARGETS_PATH) -> RepoTarget:
    with open(path, "r", encoding="utf-8") as fh:
        config = yaml.safe_load(fh) or {}
    entry = (config.get("clusters") or {}).get(cluster_name)
    if entry is None:
        raise SystemExit(
            f"No GitOps repo config for cluster {cluster_name!r} in {path}. "
            f"Add an entry under clusters:{cluster_name}: first."
        )
    merged = {**config.get("defaults", {}), **entry}
    missing = [k for k in REQUIRED_TARGET_KEYS if k not in merged]
    if missing:
        raise SystemExit(f"{path} entry for {cluster_name!r} is missing required keys: {missing}")
    return RepoTarget(
        repo_url=merged["repo_url"],
        owner=merged["owner"],
        repo_name=merged["repo_name"],
        cluster_path=merged["cluster_path"],
        curator_namespace=merged["curator_namespace"],
        base_branch=merged.get("base_branch", "main"),
        upstream_graph_url=merged.get("upstream_graph_url"),
    )


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description="Open/update a GitOps PR for a cluster's OCP upgrade")
    ap.add_argument("--cluster", required=True, help="cluster name from inventory (e.g. east-prod-01)")
    ap.add_argument("--target", required=True, help="candidate target OCP version (e.g. 4.22.8)")
    ap.add_argument("--targets-file", type=Path, default=DEFAULT_TARGETS_PATH, help="path to gitops_targets.yaml")
    ap.add_argument("--force-ready", action="store_true", help="open ready-for-review even on go-with-caveats")
    ap.add_argument("--dry-run", action="store_true", help="render everything; skip git push + GitHub API calls")
    ap.add_argument("--db-url", help="overrides DATABASE_URL")
    args = ap.parse_args()

    init_db(args.db_url)
    target = load_target(args.cluster, args.targets_file)

    token = os.environ.get("GITHUB_TOKEN")
    if not token and not args.dry_run:
        raise SystemExit("GITHUB_TOKEN is not set (or pass --dry-run to preview without it)")

    with get_session() as db:
        cluster = db.query(Cluster).filter_by(name=args.cluster).one_or_none()
        if cluster is None:
            raise SystemExit(f"Cluster {args.cluster!r} not found in inventory")

        assessment = (
            db.query(Assessment)
            .filter_by(cluster_id=cluster.id, target_version=args.target)
            .order_by(Assessment.evaluated_at.desc())
            .first()
        )
        if assessment is None:
            raise SystemExit(
                f"No assessment on file for {args.cluster} -> {args.target}. Run first:\n"
                f"  python run_assessment.py --cluster {args.cluster} --target {args.target}"
            )
        if assessment.verdict == "no-go":
            log.error("Verdict is NO-GO for %s -> %s -- refusing to open a PR.", args.cluster, args.target)
            reasons = assessment.reasons or {}
            for b in (reasons.get("blockers") or reasons.get("blocking") or []):
                detail = b.get("detail", b) if isinstance(b, dict) else b
                kind = b.get("kind") if isinstance(b, dict) else "Blocker"
                log.error("  blocking: %s: %s", kind, detail)
            raise SystemExit(1)

        try:
            result = open_or_update_pr(
                cluster_name=cluster.name,
                current_version=cluster.ocp_version,
                target_version=args.target,
                verdict=assessment.verdict,
                reasons=assessment.reasons or {},
                target=target,
                token=token or "dry-run-no-token-needed",
                assessment_id=assessment.id,
                evaluated_at=str(assessment.evaluated_at),
                force_ready=args.force_ready,
                dry_run=args.dry_run,
            )
        except requests.exceptions.HTTPError as exc:
            resp = exc.response
            raise SystemExit(
                f"GitHub API call failed: {resp.status_code} {resp.reason} for {resp.url}\n"
                f"The branch/commit was still pushed to {target.repo_url} -- fix the auth issue "
                f"(check $GITHUB_TOKEN's scopes) and re-run; it'll pick up the existing branch."
            ) from exc
        except git.exc.GitCommandError as exc:
            raise SystemExit(f"git operation failed: {exc}") from exc

    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
```

---

### `tests/__init__.py`

```python

```

---

### `tests/conftest.py`

```python
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import db.db as db_module  # noqa: E402


@pytest.fixture()
def db_session(tmp_path, monkeypatch):
    """A fresh SQLite-backed session per test, wired up as the module-level
    default so collector `collect()` functions (which call get_session()
    internally) transparently use the same test DB."""
    db_url = f"sqlite:///{tmp_path}/test.db"
    monkeypatch.setenv("DATABASE_URL", db_url)
    db_module._engine = None
    db_module._SessionLocal = None
    db_module.init_db(db_url)
    with db_module.get_session() as session:
        yield session
```

---

### `tests/fixtures/sample_cincinnati_graph.json`

```json
{
  "nodes": [
    {"version": "4.21.20", "payload": "quay.io/openshift-release-dev/ocp-release@sha256:aaa"},
    {"version": "4.21.22", "payload": "quay.io/openshift-release-dev/ocp-release@sha256:bbb"},
    {"version": "4.22.6", "payload": "quay.io/openshift-release-dev/ocp-release@sha256:ccc"},
    {"version": "4.22.8", "payload": "quay.io/openshift-release-dev/ocp-release@sha256:ddd"}
  ],
  "edges": [[0, 1], [1, 2], [2, 3]],
  "conditionalEdges": [
    {
      "edges": [{"from": "4.21.22", "to": "4.22.6"}],
      "risks": [
        {
          "url": "https://bugzilla.redhat.com/show_bug.cgi?id=2345111",
          "name": "MultipathSCSIQueueDepth",
          "message": "Clusters with multipath-configured SCSI devices may see degraded I/O throughput immediately after this update.",
          "matchingRules": [
            {"type": "PromQL", "promql": {"promql": "count(node_multipath_scsi_enabled) > 0"}}
          ]
        }
      ]
    }
  ]
}
```

---

### `tests/fixtures/sample_clusterversion.json`

```json
{
  "apiVersion": "config.openshift.io/v1",
  "kind": "ClusterVersion",
  "metadata": {"name": "version"},
  "spec": {"channel": "stable-4.21", "clusterID": "abc-123"},
  "status": {
    "desired": {"version": "4.21.22", "image": "quay.io/openshift-release-dev/ocp-release@sha256:bbb"},
    "availableUpdates": [
      {"version": "4.21.24", "image": "quay.io/openshift-release-dev/ocp-release@sha256:eee"}
    ],
    "conditionalUpdates": [
      {
        "release": {"version": "4.22.6"},
        "risks": [
          {
            "url": "https://bugzilla.redhat.com/show_bug.cgi?id=2345111",
            "name": "MultipathSCSIQueueDepth",
            "message": "This cluster is running multipath-configured SCSI devices matching the affected pattern.",
            "matchingRules": [
              {"type": "PromQL", "promql": {"promql": "count(node_multipath_scsi_enabled) > 0"}}
            ]
          }
        ]
      }
    ]
  }
}
```

---

### `tests/fixtures/sample_csaf.json`

```json
[
  {
    "id": "RHSA-2026:29834",
    "title": "Important: OpenShift Container Platform 4.21.22 security update",
    "severity": "important",
    "current_release_date": "2026-07-10T00:00:00Z",
    "initial_release_date": "2026-07-10T00:00:00Z",
    "self_href": "https://access.redhat.com/errata/RHSA-2026:29834"
  }
]
```

---

### `tests/fixtures/sample_csvs.json`

```json
[
  {
    "metadata": {"name": "kubevirt-hyperconverged-operator.v4.21.3", "namespace": "openshift-cnv"},
    "spec": {"version": "4.21.3"},
    "status": {"phase": "Succeeded"}
  },
  {
    "metadata": {"name": "dell-csm-operator.v1.9.2", "namespace": "dell-csm-operator"},
    "spec": {"version": "1.9.2"},
    "status": {"phase": "Succeeded"}
  },
  {
    "metadata": {"name": "portworx-operator.v25.3.0", "namespace": "portworx"},
    "spec": {"version": "25.3.0"},
    "status": {"phase": "Succeeded"}
  },
  {
    "metadata": {"name": "cert-manager-operator.v1.14.0", "namespace": "cert-manager-operator"},
    "spec": {"version": "1.14.0"},
    "status": {"phase": "Succeeded"}
  },
  {
    "metadata": {"name": "some-broken-operator.v1.0.0", "namespace": "some-ns"},
    "spec": {"version": "1.0.0"},
    "status": {"phase": "Failed"}
  }
]
```

---

### `tests/fixtures/sample_cve.json`

```json
[
  {
    "CVE": "CVE-2026-31431",
    "severity": "important",
    "public_date": "2026-06-15T00:00:00Z",
    "bugzilla": {"id": "2345678", "description": "kernel: use-after-free in multipath subsystem"},
    "resource_url": "https://access.redhat.com/hydra/rest/securitydata/cve/CVE-2026-31431.json",
    "cvss3": {"cvss3_base_score": "8.1"},
    "affected_packages": ["kernel-0:5.14.0-503.el9"]
  },
  {
    "CVE": "CVE-2026-43284",
    "severity": "critical",
    "public_date": "2026-07-02T00:00:00Z",
    "bugzilla": {"id": "2345999", "description": "runc: container escape via crafted OCI image"},
    "resource_url": "https://access.redhat.com/hydra/rest/securitydata/cve/CVE-2026-43284.json",
    "cvss3": {"cvss3_base_score": "9.3"},
    "affected_packages": ["runc-0:1.1.12-1.el9"]
  }
]
```

---

### `tests/fixtures/sample_lifecycle.json`

```json
{
  "data": [
    {
      "name": "Openshift Container Platform 4",
      "version": "4.20",
      "type": "OpenShift",
      "phase": [
        {"name": "General availability", "date": "2026-02-25"},
        {"name": "Full support", "date": "2026-02-25"},
        {"name": "Maintenance support", "date": "2027-08-25"},
        {"name": "End of life", "date": "2028-02-25"}
      ]
    },
    {
      "name": "Openshift Container Platform 4",
      "version": "4.22",
      "type": "OpenShift",
      "phase": [
        {"name": "General availability", "date": "2026-06-09"},
        {"name": "Full support", "date": "2026-06-09"},
        {"name": "Maintenance support", "date": "2027-12-09"},
        {"name": "End of life", "date": "2028-06-09"}
      ]
    }
  ]
}
```

---

### `tests/fixtures/sample_release_info.json`

```json
{
  "metadata": {"version": "4.22.8"},
  "digest": "sha256:eeeeeeee",
  "references": {
    "kind": "ImageStream",
    "apiVersion": "image.openshift.io/v1",
    "spec": {
      "tags": [
        {
          "name": "cluster-version-operator",
          "from": {"kind": "DockerImage", "name": "quay.io/openshift-release-dev/ocp-v4.0-art-dev@sha256:111"}
        },
        {
          "name": "kubevirt-hyperconverged-operator",
          "from": {"kind": "DockerImage", "name": "quay.io/openshift-release-dev/ocp-v4.0-art-dev@sha256:222"}
        }
      ]
    }
  }
}
```

---

### `tests/test_cincinnati.py`

```python
from collectors.cincinnati import parse_edges, upsert_edges
from db.models import UpgradeEdge
from tests.utils import load_fixture


def test_parse_edges_splits_unconditional_and_conditional():
    graph = load_fixture("sample_cincinnati_graph.json")
    rows = parse_edges(graph, channel="stable-4.22", arch="amd64")

    unconditional = [r for r in rows if not r["conditional"]]
    conditional = [r for r in rows if r["conditional"]]
    assert len(unconditional) == 3
    assert len(conditional) == 1

    risk = conditional[0]
    assert (risk["from_version"], risk["to_version"]) == ("4.21.22", "4.22.6")
    assert risk["risk_name"] == "MultipathSCSIQueueDepth"
    assert risk["matching_rule"][0]["type"] == "PromQL"


def test_upsert(db_session):
    graph = load_fixture("sample_cincinnati_graph.json")
    rows = parse_edges(graph, channel="stable-4.22", arch="amd64")
    n = upsert_edges(db_session, rows)
    db_session.commit()
    assert n == 4
    assert db_session.query(UpgradeEdge).count() == 4
```

---

### `tests/test_cluster_state.py`

```python
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
```

---

### `tests/test_gitops.py`

```python
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from ruamel.yaml import YAML

from gitops.bot import (
    RepoTarget,
    create_yaml_parser,
    open_or_update_pr,
    render_pr_body,
    update_cluster_manifests,
)
from run_gitops_pr import load_target

TARGETS_FILE = Path(__file__).resolve().parents[1] / "data" / "gitops_targets.yaml"


def test_load_target_success():
    target = load_target("east-prod-01", TARGETS_FILE)
    assert isinstance(target, RepoTarget)
    assert target.owner == "example-org"
    assert target.repo_name == "ocp-gitops-fleet"
    assert target.cluster_path == "clusters/east-prod-01"
    assert target.curator_namespace == "east-prod-01"
    assert target.upstream_graph_url == "http://cincinnati.internal.net/api/upgrades_info/v1/graph"


def test_load_target_missing():
    with pytest.raises(SystemExit) as exc:
        load_target("nonexistent-cluster", TARGETS_FILE)
    assert "No GitOps repo config" in str(exc.value)


def test_update_cluster_manifests_preserves_comments(tmp_path):
    repo_root = tmp_path / "repo"
    cluster_dir = repo_root / "clusters" / "east-prod-01"
    cluster_dir.mkdir(parents=True)

    curator_file = cluster_dir / "cluster-curator.yaml"
    curator_content = """# ClusterCurator configuration for ACM fleet upgrades
apiVersion: cluster.open-cluster-management.io/v1beta1
kind: ClusterCurator
metadata:
  name: east-prod-01
  namespace: east-prod-01 # ACM cluster namespace
spec:
  desiredCuration: none
  upgrade:
    channel: stable-4.21 # Track stable channel
    desiredUpdate: "4.21.5"
"""
    curator_file.write_text(curator_content, encoding="utf-8")

    target = RepoTarget(
        repo_url="https://github.com/example-org/ocp-gitops-fleet.git",
        owner="example-org",
        repo_name="ocp-gitops-fleet",
        cluster_path="clusters/east-prod-01",
        curator_namespace="east-prod-01",
    )

    modified = update_cluster_manifests(repo_root, target, "east-prod-01", "4.22.8")
    assert len(modified) == 1
    assert "cluster-curator.yaml" in modified[0]

    updated_text = curator_file.read_text(encoding="utf-8")
    assert "ClusterCurator configuration for ACM fleet upgrades" in updated_text
    assert "# ACM cluster namespace" in updated_text
    assert 'desiredUpdate: "4.22.8"' in updated_text or "desiredUpdate: 4.22.8" in updated_text
    assert "desiredCuration: upgrade" in updated_text


def test_update_cluster_manifests_creates_new(tmp_path):
    repo_root = tmp_path / "repo"
    target = RepoTarget(
        repo_url="https://github.com/example-org/ocp-gitops-fleet.git",
        owner="example-org",
        repo_name="ocp-gitops-fleet",
        cluster_path="clusters/west-prod-01",
        curator_namespace="west-prod-01",
    )

    modified = update_cluster_manifests(repo_root, target, "west-prod-01", "4.22.8")
    assert len(modified) == 1
    created_file = repo_root / modified[0]
    assert created_file.exists()

    y = YAML()
    doc = y.load(created_file.read_text(encoding="utf-8"))
    assert doc["kind"] == "ClusterCurator"
    assert doc["spec"]["desiredCuration"] == "upgrade"
    assert doc["spec"]["upgrade"]["desiredUpdate"] == "4.22.8"


def test_render_pr_body():
    body = render_pr_body(
        cluster_name="east-prod-01",
        current_version="4.21.5",
        target_version="4.22.8",
        verdict="go-with-caveats",
        reasons={
            "caveats": ["Multus CNI conditional update notice"],
            "info": ["Upgrade path verified in Cincinnati graph"],
        },
        assessment_id=42,
        evaluated_at="2026-08-17T07:00:00Z",
    )
    assert "Automated Pre-Upgrade Assessment — east-prod-01" in body
    assert "4.21.5" in body
    assert "4.22.8" in body
    assert "GO WITH CAVEATS" in body
    assert "Multus CNI conditional update notice" in body
    assert "Pre-Merge Checklist" in body


def test_open_or_update_pr_dry_run():
    target = RepoTarget(
        repo_url="https://github.com/example-org/ocp-gitops-fleet.git",
        owner="example-org",
        repo_name="ocp-gitops-fleet",
        cluster_path="clusters/east-prod-01",
        curator_namespace="east-prod-01",
    )

    res = open_or_update_pr(
        cluster_name="east-prod-01",
        current_version="4.21.5",
        target_version="4.22.8",
        verdict="go",
        reasons={"info": ["Path verified"]},
        target=target,
        token="test-token",
        assessment_id=1,
        evaluated_at="2026-08-17T07:00:00Z",
        dry_run=True,
    )

    assert res["action"] == "dry-run-preview"
    assert res["cluster"] == "east-prod-01"
    assert res["target_version"] == "4.22.8"
    assert res["branch"] == "upgrade/east-prod-01-to-4.22.8"
    assert res["draft"] is False
    assert len(res["modified_files"]) > 0
    assert "diff" in res
```

---

### `tests/test_lifecycle.py`

```python
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
```

---

### `tests/test_redhat_security.py`

```python
from collectors.redhat_security import _parse_cve_item, _parse_csaf_item, upsert_advisories
from db.models import Advisory
from tests.utils import load_fixture


def test_parse_cve_item():
    items = load_fixture("sample_cve.json")
    row = _parse_cve_item(items[0], "ocp")
    assert row["source"] == "redhat-cve"
    assert row["external_id"] == "CVE-2026-31431"
    assert row["severity"] == "important"
    assert row["affected_component"] == "ocp"
    assert row["published_at"].year == 2026
    assert row["url"].endswith("CVE-2026-31431.json")


def test_parse_csaf_item():
    items = load_fixture("sample_csaf.json")
    row = _parse_csaf_item(items[0], "ocp")
    assert row["source"] == "redhat-errata"
    assert row["external_id"] == "RHSA-2026:29834"
    assert row["severity"] == "important"


def test_upsert_then_reupsert_updates_in_place(db_session):
    items = load_fixture("sample_cve.json")
    rows = [_parse_cve_item(i, "ocp") for i in items]

    n = upsert_advisories(db_session, rows)
    db_session.commit()
    assert n == 2
    assert db_session.query(Advisory).count() == 2

    rows[0]["severity"] = "critical"
    upsert_advisories(db_session, rows)
    db_session.commit()

    assert db_session.query(Advisory).count() == 2  # no duplicate row
    updated = db_session.query(Advisory).filter_by(external_id="CVE-2026-31431").one()
    assert updated.severity == "critical"
```

---

### `tests/test_release_info.py`

```python
from collectors.release_info import parse_release_images, upsert_release_images
from db.models import ReleaseImage
from tests.utils import load_fixture


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
```

---

### `tests/test_vendor_matrix.py`

```python
from pathlib import Path

from collectors.vendor_matrix import collect, load_seed
from db.models import Advisory, OperatorCompat

SEED = Path(__file__).resolve().parents[1] / "data" / "vendor_matrix_seed.yaml"


def test_load_seed_shape():
    data = load_seed(SEED)
    assert len(data["operator_compat"]) >= 2
    assert len(data["known_bugs"]) >= 1
    assert any(b["external_id"] == "PWX-46691" for b in data["known_bugs"])


def test_collect_writes_both_tables(db_session):
    n_compat, n_bugs = collect(SEED)
    assert n_compat >= 2
    assert n_bugs >= 1
    assert db_session.query(OperatorCompat).filter_by(component="dell-csm").count() >= 1
    assert db_session.query(Advisory).filter_by(source="portworx", external_id="PWX-46691").count() == 1
```

---

### `tests/utils.py`

```python
import json
from pathlib import Path

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def load_fixture(name: str):
    with open(FIXTURES_DIR / name) as fh:
        return json.load(fh)
```

---

