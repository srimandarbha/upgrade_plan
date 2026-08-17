#!/usr/bin/env python3
"""Generate a single consolidated PROJECT_BUNDLE.md containing all files, tree, and outputs."""
import os

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_file = os.path.join(root_dir, "PROJECT_BUNDLE.md")

excluded_dirs = {".git", "venv", ".venv", "__pycache__", "scripts"}
excluded_files = {"ocv_agent.db", "PROJECT_BUNDLE.md"}

files_to_bundle = []
for dirpath, dirnames, filenames in os.walk(root_dir):
    dirnames[:] = [d for d in dirnames if d not in excluded_dirs]
    for f in sorted(filenames):
        if f in excluded_files or f.endswith(".pyc"):
            continue
        rel_path = os.path.relpath(os.path.join(dirpath, f), root_dir).replace("\\", "/")
        files_to_bundle.append((rel_path, os.path.join(dirpath, f)))

files_to_bundle.sort(key=lambda x: x[0])

with open(output_file, "w", encoding="utf-8") as out:
    out.write("# Complete Project Codebase Bundle & Execution Log\n\n")
    out.write("**Project Name:** OpenShift Virtualization (OCV) Pre-Upgrade & Migration Assessment Agent\n\n")
    out.write("**Repository:** `srimandarbha/upgrade_plan`\n\n")
    out.write("This single document contains the complete project tree, all source code files, configurations, database schemas, test fixtures, and live execution outputs.\n\n")
    
    out.write("## Table of Contents\n\n")
    out.write("1. [Directory Tree](#directory-tree)\n")
    out.write("2. [Live Terminal Execution Outputs](#live-terminal-execution-outputs)\n")
    out.write("3. [Source Code & Configuration Files](#source-code--configuration-files)\n")
    for rel_path, _ in files_to_bundle:
        out.write(f"   - [`{rel_path}`](#{rel_path.replace('/', '').replace('.', '').replace('_', '-').lower()})\n")
    out.write("\n---\n\n")

    out.write("## Directory Tree\n\n```text\nocv-upgrade-agent/\n")
    for rel_path, _ in files_to_bundle:
        out.write(f"  ├── {rel_path}\n")
    out.write("```\n\n---\n\n")

    out.write("## Live Terminal Execution Outputs\n\n")

    out.write("### 1. Collector Execution (PostgreSQL)\n\n```text\n")
    out.write("PS > python run_collectors.py --only redhat-security,cincinnati,lifecycle,vendor-matrix\n\n")
    out.write("2026-08-16 21:34:45 INFO __main__: --- running redhat-security ---\n")
    out.write("2026-08-16 21:34:47 INFO __main__: --- redhat-security done: 1000 ---\n")
    out.write("2026-08-16 21:34:47 INFO __main__: --- running cincinnati ---\n")
    out.write("2026-08-16 21:34:51 INFO __main__: --- cincinnati done: 2494 ---\n")
    out.write("2026-08-16 21:35:58 INFO __main__: --- running lifecycle ---\n")
    out.write("2026-08-16 21:36:00 INFO __main__: --- lifecycle done: 1 ---\n")
    out.write("2026-08-16 21:36:00 INFO __main__: --- running vendor-matrix ---\n")
    out.write("2026-08-16 22:00:27 INFO __main__: --- vendor-matrix done: (9, 3) ---\n")
    out.write("```\n\n")

    out.write("### 2. PostgreSQL Row Verification\n\n```text\n")
    out.write("PS > psql -U postgres -h localhost -d ocv_agent -c 'SELECT table_name, count FROM ...'\n\n")
    out.write("    table_name     | count \n")
    out.write("-------------------+-------\n")
    out.write(" advisories        |  1001\n")
    out.write(" upgrade_edges     |  3962\n")
    out.write(" product_lifecycle |     1\n")
    out.write(" operator_compat   |     9\n")
    out.write("```\n\n")

    out.write("### 3. Scenario A: Safe z-Stream Assessment (Verdict: GO)\n\n```text\n")
    out.write("PS > python run_assessment.py --cluster east-prod-01 --target 4.22.8\n\n")
    out.write("======================================================================\n")
    out.write("UPGRADE ASSESSMENT RESULT: GO\n")
    out.write("======================================================================\n\n")
    out.write("--- [RAW AUDIT JSON PAYLOAD] ---\n")
    out.write("{\n")
    out.write('  "cluster": "east-prod-01",\n')
    out.write('  "current_version": "4.22.2",\n')
    out.write('  "target_version": "4.22.8",\n')
    out.write('  "deterministic_verdict": "GO",\n')
    out.write('  "reasons": {\n')
    out.write('    "info": [\n')
    out.write('      "Upgrade path from 4.22.2 to 4.22.8 exists in Cincinnati graph.",\n')
    out.write('      "Operator \'mtv\' version 2.8.0 verified compatible with 4.22.8.",\n')
    out.write('      "Operator \'dell-csm\' version 1.11.0 verified compatible with 4.22.8.",\n')
    out.write('      "Operator \'portworx\' version 25.3.0 verified compatible with 4.22.8."\n')
    out.write("    ],\n")
    out.write('    "caveats": [],\n')
    out.write('    "verdict": "go",\n')
    out.write('    "blockers": [],\n')
    out.write('    "target_version": "4.22.8",\n')
    out.write('    "current_version": "4.22.2"\n')
    out.write("  },\n")
    out.write('  "evaluated_at": "2026-08-16T22:18:39.512784+05:30"\n')
    out.write("}\n")
    out.write("```\n\n")

    out.write("### 4. Scenario B: Major Drift Jump to 5.0.0 (Verdict: NO-GO ESCALATE)\n\n```text\n")
    out.write("PS > python run_assessment.py --cluster east-prod-01 --target 5.0.0 --llm\n\n")
    out.write("======================================================================\n")
    out.write("UPGRADE ASSESSMENT RESULT: NO-GO (ESCALATE)\n")
    out.write("======================================================================\n\n")
    out.write("--- [EXECUTIVE SYNOPSIS] ---\n")
    out.write("RECOMMENDATION: HOLD UPGRADE (NO-GO ESCALATED). Upgrading cluster 'east-prod-01' from OCP 4.22.2 to 5.0.0 poses high operational risk to active migration and storage workloads. Identified 5 primary blocker(s) including version drift and operator boundary mismatches. Platform SRE and TestOps sign-off is strictly required prior to staging validation.\n\n")
    out.write("--- [ESCALATION & BLOCKER TRIGGERS] ---\n")
    out.write(" • Major version architectural drift detected (4.22.2 -> 5.0.0). Under TestOps Policy TESTOPS-POL-4082, major version transitions require mandatory sandbox qualification.\n")
    out.write(" • mtv (version 2.8.0) is NOT certified for OCP 5.0.0 (supported up to 4.22).\n")
    out.write(" • dell-csm (version 1.11.0) is NOT certified for OCP 5.0.0 (supported up to 4.22).\n")
    out.write(" • portworx (version 25.3.0) is NOT certified for OCP 5.0.0 (supported up to 4.22).\n")
    out.write(" • Active MTV (Migration Toolkit for Virtualization) operator v2.8.0 detected. VM migration stability is prioritized over routine platform upgrades unless critical CVEs are unpatched.\n\n")
    out.write("--- [DEEP COMPONENT & STORAGE IMPACT] ---\n")
    out.write(" • MIGRATION_IMPACT (MTV): HIGH RISK: Major/unsupported OCP version jump may break virt-v2v controller status streams, warm migration changed block tracking (CBT), and vSphere VDDK disk transfer pipes.\n")
    out.write(" • STORAGE_IMPACT (DELL CSM & PORTWORX): CRITICAL RISK: Storage CSI drivers (dell-csm, portworx) require kernel header validation and CSI node-driver re-certification on target Kubernetes base.\n")
    out.write(" • SECURITY_DELTA: 30 Critical and 832 Important CVE/RHSAs tracked in database. Target 5.0.0 incorporates recent security patches.\n\n")
    out.write("--- [TESTOPS REMEDIATION & QUALIFICATION PLAN] ---\n")
    out.write(" Step 1 [Pre-Requisite Operator Upgrades]:\n")
    out.write("   Action: Upgrade MTV to certified operator version (e.g. 2.8.0+) and Dell CSM / Portworx to latest supported z-stream in Pre-Prod.\n")
    out.write("   Gate:   Operator CSVs in Succeeded phase with 0 CrashLoopBackOff pods.\n")
    out.write(" Step 2 [Staging Sandbox Live Migration Test]:\n")
    out.write("   Action: Execute end-to-end VM warm migration dry run from VMware vSphere to OCV on target OCP build.\n")
    out.write("   Gate:   Zero data corruption, successful cutover under 60 seconds.\n")
    out.write(" Step 3 [CSI Storage Failover Verification]:\n")
    out.write("   Action: Trigger node drain and worker reboot while running I/O load on Dell CSM (PowerStore/PowerFlex) and Portworx RWX volumes.\n")
    out.write("   Gate:   Volumes reattach within 30s without VolumeAttachment timeout.\n")
    out.write(" Step 4 [Fleet Canary Deployment]:\n")
    out.write("   Action: Roll out upgrade to 1 non-prod lab cluster before scheduling production fleet windows.\n")
    out.write("   Gate:   ClusterVersion reaches Available=True with 0 cluster operator degraded alerts for 48 hours.\n\n")
    out.write("--- [HUMAN-IN-THE-LOOP SIGN-OFF GATE] ---\n")
    out.write(" Status: PENDING_APPROVAL\n")
    out.write(" Required Approvers: TestOps Lead, Cloud Platform SRE Lead, Storage Administrator\n")
    out.write(" Checklist:\n")
    out.write("   [ ] All active MTV VM migrations paused / drained\n")
    out.write("   [ ] Dell CSM / Portworx sandbox failover test passed\n")
    out.write("   [ ] TestOps qualification test suite executed on target build\n")
    out.write("   [ ] Maintenance window approved by Change Advisory Board (CAB)\n")
    out.write("```\n\n")

    out.write("### 5. Automated GitOps PR Dry-Run (ACM ClusterCurator Manifest Bump)\n\n```text\n")
    out.write("PS > python run_gitops_pr.py --cluster east-prod-01 --target 4.22.8 --dry-run\n\n")
    out.write("2026-08-17 07:57:58 INFO gitops.bot: [DRY-RUN] Simulating GitOps PR creation for east-prod-01 -> 4.22.8\n")
    out.write("2026-08-17 07:57:58 INFO gitops.bot: Created new ClusterCurator manifest at clusters/east-prod-01/cluster-curator.yaml\n")
    out.write("{\n")
    out.write('  "action": "dry-run-preview",\n')
    out.write('  "cluster": "east-prod-01",\n')
    out.write('  "current_version": "4.22.2",\n')
    out.write('  "target_version": "4.22.8",\n')
    out.write('  "verdict": "go",\n')
    out.write('  "branch": "upgrade/east-prod-01-to-4.22.8",\n')
    out.write('  "base_branch": "main",\n')
    out.write('  "draft": false,\n')
    out.write('  "pr_title": "feat(gitops): upgrade east-prod-01 to OCP 4.22.8 [GO]",\n')
    out.write('  "modified_files": [\n')
    out.write('    "clusters/east-prod-01/cluster-curator.yaml"\n')
    out.write('  ],\n')
    out.write('  "diff": "diff --git a/clusters/east-prod-01/cluster-curator.yaml b/clusters/east-prod-01/cluster-curator.yaml\\nnew file mode 100644\\n--- /dev/null\\n+++ b/clusters/east-prod-01/cluster-curator.yaml\\n@@ -0,0 +1,13 @@\\n+apiVersion: cluster.open-cluster-management.io/v1beta1\\n+kind: ClusterCurator\\n+metadata:\\n+  name: east-prod-01\\n+  namespace: east-prod-01\\n+  labels:\\n+    open-cluster-management.io/cluster-name: east-prod-01\\n+spec:\\n+  desiredCuration: upgrade\\n+  upgrade:\\n+    channel: stable-4.22\\n+    desiredUpdate: 4.22.8\\n+    upstream: http://cincinnati.internal.net/api/upgrades_info/v1/graph"\n')
    out.write("}\n")
    out.write("```\n\n---\n\n")

    out.write("## Source Code & Configuration Files\n\n")
    for rel_path, full_path in files_to_bundle:
        ext = rel_path.split(".")[-1].lower() if "." in rel_path else ""
        lang_map = {
            "py": "python",
            "sql": "sql",
            "yaml": "yaml",
            "yml": "yaml",
            "json": "json",
            "md": "markdown",
            "txt": "text",
            "env": "bash",
            "example": "bash",
        }
        lang = lang_map.get(ext, "")
        out.write(f"### `{rel_path}`\n\n")
        out.write(f"```{lang}\n")
        with open(full_path, "r", encoding="utf-8", errors="replace") as sf:
            content = sf.read()
            out.write(content)
            if not content.endswith("\n"):
                out.write("\n")
        out.write("```\n\n---\n\n")

print(f"Successfully generated {output_file}")
