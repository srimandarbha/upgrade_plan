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
