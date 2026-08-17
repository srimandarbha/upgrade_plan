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
