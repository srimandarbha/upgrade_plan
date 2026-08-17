-- =============================================================================
-- OpenShift Virtualization (OCV) Upgrade Agent - PostgreSQL Production Seed
-- Cluster Source: 4.20.0 | Target Trajectory: 4.21.x -> 4.22.0 .. 4.22.8
-- Disconnected / Air-Gapped Environment Ready
-- =============================================================================

BEGIN;

-- 1. Ensure Schema Exists
CREATE TABLE IF NOT EXISTS clusters (
    id                  SERIAL PRIMARY KEY,
    name                TEXT NOT NULL UNIQUE,
    region              TEXT NOT NULL,
    env                 TEXT NOT NULL DEFAULT 'prod',
    ocp_version         TEXT NOT NULL,
    api_url             TEXT,
    kubeconfig_context  TEXT,
    connected           BOOLEAN NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS component_versions (
    id              SERIAL PRIMARY KEY,
    cluster_id      INTEGER NOT NULL REFERENCES clusters(id) ON DELETE CASCADE,
    component       TEXT NOT NULL,
    version         TEXT NOT NULL,
    channel         TEXT,
    namespace       TEXT,
    csv_name        TEXT,
    observed_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (cluster_id, component)
);

CREATE TABLE IF NOT EXISTS advisories (
    id                      SERIAL PRIMARY KEY,
    source                  TEXT NOT NULL,
    external_id             TEXT NOT NULL,
    title                   TEXT NOT NULL,
    severity                TEXT,
    affected_component      TEXT,
    affected_version_range  TEXT,
    published_at            TIMESTAMPTZ,
    url                     TEXT,
    fetched_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    raw                     JSONB,
    UNIQUE (source, external_id)
);

CREATE TABLE IF NOT EXISTS operator_compat (
    id                  SERIAL PRIMARY KEY,
    component           TEXT NOT NULL,
    operator_version    TEXT NOT NULL,
    min_ocp             TEXT,
    max_ocp             TEXT,
    source              TEXT NOT NULL,
    verified_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    notes               TEXT,
    UNIQUE (component, operator_version, source)
);

CREATE TABLE IF NOT EXISTS product_lifecycle (
    id                  SERIAL PRIMARY KEY,
    component           TEXT NOT NULL,
    version             TEXT NOT NULL,
    phase               TEXT,
    ga_date             DATE,
    full_support_end    DATE,
    maintenance_end     DATE,
    eol_date            DATE,
    fetched_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (component, version)
);

CREATE TABLE IF NOT EXISTS upgrade_edges (
    id              SERIAL PRIMARY KEY,
    channel         TEXT NOT NULL,
    arch            TEXT NOT NULL DEFAULT 'amd64',
    from_version    TEXT NOT NULL,
    to_version      TEXT NOT NULL,
    conditional     BOOLEAN NOT NULL DEFAULT FALSE,
    risk_name       TEXT,
    risk_message    TEXT,
    matching_rule   JSONB,
    fetched_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (channel, arch, from_version, to_version, risk_name)
);

CREATE TABLE IF NOT EXISTS release_images (
    id          SERIAL PRIMARY KEY,
    component   TEXT NOT NULL,
    version     TEXT NOT NULL,
    image       TEXT NOT NULL,
    fetched_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (version, component)
);

CREATE TABLE IF NOT EXISTS assessments (
    id              SERIAL PRIMARY KEY,
    cluster_id      INTEGER NOT NULL REFERENCES clusters(id) ON DELETE CASCADE,
    target_version  TEXT NOT NULL,
    verdict         TEXT NOT NULL,
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

-- Indexes
CREATE INDEX IF NOT EXISTS idx_advisories_component ON advisories (affected_component);
CREATE INDEX IF NOT EXISTS idx_operator_compat_component ON operator_compat (component);
CREATE INDEX IF NOT EXISTS idx_upgrade_edges_from ON upgrade_edges (channel, arch, from_version);
CREATE INDEX IF NOT EXISTS idx_component_versions_cluster ON component_versions (cluster_id);
CREATE INDEX IF NOT EXISTS idx_component_versions_component ON component_versions (component);
CREATE INDEX IF NOT EXISTS idx_assessments_cluster ON assessments (cluster_id);

-- =============================================================================
-- 2. Fleet Inventory: Cluster at 4.20.0 and Installed Component Versions
-- =============================================================================
INSERT INTO clusters (name, region, env, ocp_version, connected)
VALUES 
    ('ocp-prod-dc1', 'us-east-1', 'prod', '4.20.0', FALSE),
    ('ocp-stage-dc1', 'us-east-1', 'non-prod', '4.20.0', FALSE)
ON CONFLICT (name) DO UPDATE SET ocp_version = EXCLUDED.ocp_version, updated_at = now();

-- Production Cluster (4.20.0 baseline)
INSERT INTO component_versions (cluster_id, component, version, channel, namespace, csv_name)
SELECT id, 'ocp', '4.20.0', 'stable-4.20', 'openshift-cluster-version', 'cluster-version-operator.v4.20.0'
FROM clusters WHERE name = 'ocp-prod-dc1'
ON CONFLICT (cluster_id, component) DO UPDATE SET version = EXCLUDED.version, observed_at = now();

INSERT INTO component_versions (cluster_id, component, version, channel, namespace, csv_name)
SELECT id, 'ocv', '4.20.0', 'stable-4.20', 'openshift-cnv', 'kubevirt-hyperconverged.v4.20.0'
FROM clusters WHERE name = 'ocp-prod-dc1'
ON CONFLICT (cluster_id, component) DO UPDATE SET version = EXCLUDED.version, observed_at = now();

INSERT INTO component_versions (cluster_id, component, version, channel, namespace, csv_name)
SELECT id, 'dell-csm', '1.13.0', 'stable', 'dell-csm', 'dell-csm-operator.v1.13.0'
FROM clusters WHERE name = 'ocp-prod-dc1'
ON CONFLICT (cluster_id, component) DO UPDATE SET version = EXCLUDED.version, observed_at = now();

INSERT INTO component_versions (cluster_id, component, version, channel, namespace, csv_name)
SELECT id, 'portworx', '3.1.4', 'stable', 'portworx', 'portworx-operator.v3.1.4'
FROM clusters WHERE name = 'ocp-prod-dc1'
ON CONFLICT (cluster_id, component) DO UPDATE SET version = EXCLUDED.version, observed_at = now();

-- Staging Cluster (4.20.0 baseline)
INSERT INTO component_versions (cluster_id, component, version, channel, namespace, csv_name)
SELECT id, 'ocp', '4.20.0', 'stable-4.20', 'openshift-cluster-version', 'cluster-version-operator.v4.20.0'
FROM clusters WHERE name = 'ocp-stage-dc1'
ON CONFLICT (cluster_id, component) DO UPDATE SET version = EXCLUDED.version, observed_at = now();

INSERT INTO component_versions (cluster_id, component, version, channel, namespace, csv_name)
SELECT id, 'ocv', '4.20.0', 'stable-4.20', 'openshift-cnv', 'kubevirt-hyperconverged.v4.20.0'
FROM clusters WHERE name = 'ocp-stage-dc1'
ON CONFLICT (cluster_id, component) DO UPDATE SET version = EXCLUDED.version, observed_at = now();

INSERT INTO component_versions (cluster_id, component, version, channel, namespace, csv_name)
SELECT id, 'dell-csm', '1.13.0', 'stable', 'dell-csm', 'dell-csm-operator.v1.13.0'
FROM clusters WHERE name = 'ocp-stage-dc1'
ON CONFLICT (cluster_id, component) DO UPDATE SET version = EXCLUDED.version, observed_at = now();

INSERT INTO component_versions (cluster_id, component, version, channel, namespace, csv_name)
SELECT id, 'portworx', '3.1.4', 'stable', 'portworx', 'portworx-operator.v3.1.4'
FROM clusters WHERE name = 'ocp-stage-dc1'
ON CONFLICT (cluster_id, component) DO UPDATE SET version = EXCLUDED.version, observed_at = now();

-- =============================================================================
-- 3. Product Lifecycle (Red Hat OCP & OCV 4.20, 4.21, 4.22)
-- =============================================================================
INSERT INTO product_lifecycle (component, version, phase, ga_date, full_support_end, maintenance_end, eol_date)
VALUES
    ('ocp', '4.20', 'Full Support', '2025-10-15', '2026-04-15', '2026-10-15', '2027-04-15'),
    ('ocp', '4.21', 'Full Support', '2026-02-20', '2026-08-20', '2027-02-20', '2027-08-20'),
    ('ocp', '4.22', 'Full Support', '2026-06-10', '2026-12-10', '2027-06-10', '2027-12-10'),
    ('ocv', '4.20', 'Full Support', '2025-10-25', '2026-04-25', '2026-10-25', '2027-04-25'),
    ('ocv', '4.21', 'Full Support', '2026-02-28', '2026-08-28', '2027-02-28', '2027-08-28'),
    ('ocv', '4.22', 'Full Support', '2026-06-18', '2026-12-18', '2027-06-18', '2027-12-18')
ON CONFLICT (component, version) DO UPDATE SET
    phase = EXCLUDED.phase,
    ga_date = EXCLUDED.ga_date,
    full_support_end = EXCLUDED.full_support_end,
    maintenance_end = EXCLUDED.maintenance_end,
    eol_date = EXCLUDED.eol_date,
    fetched_at = now();

-- =============================================================================
-- 4. Operator Compatibility Matrix (OCV/CNV, Dell CSM, Portworx across OCP 4.20 -> 4.22)
-- =============================================================================
INSERT INTO operator_compat (component, operator_version, min_ocp, max_ocp, source, notes)
VALUES
    -- OpenShift Virtualization (OCV)
    ('ocv', '4.20.0', '4.20.0', '4.20.99', 'olm-catalog', 'Aligned with OCP 4.20 minor stream'),
    ('ocv', '4.21.0', '4.21.0', '4.21.99', 'olm-catalog', 'Supports OCP 4.21 with live-migration enhancements'),
    ('ocv', '4.22.0', '4.22.0', '4.22.99', 'olm-catalog', 'Requires OCP 4.22.0+ for VirtIO modern drivers and KubeVirt v1.4+'),
    
    -- Dell CSM
    ('dell-csm', '1.13.0', '4.17.0', '4.20.99', 'dell-csm-support-matrix', 'Supported on OCP 4.18-4.20; unsupported on OCP 4.21+'),
    ('dell-csm', '1.14.0', '4.19.0', '4.21.99', 'dell-csm-support-matrix', 'Introduces support for OCP 4.21; required prior to OCP 4.21 upgrade'),
    ('dell-csm', '1.15.0', '4.20.0', '4.22.99', 'dell-csm-support-matrix', 'Full support for OCP 4.22.x; required before upgrading OCP past 4.21'),
    
    -- Portworx
    ('portworx', '3.1.4', '4.16.0', '4.20.99', 'portworx-support-matrix', 'Certified up to OCP 4.20; kernel module panic reported on OCP 4.21 kernel 6.6+'),
    ('portworx', '3.2.0', '4.19.0', '4.21.99', 'portworx-support-matrix', 'Compatible with OCP 4.21; includes kernel 6.6 eBPF hooks'),
    ('portworx', '3.3.0', '4.20.0', '4.22.99', 'portworx-support-matrix', 'Full OCP 4.22 support including OCV VM disk persistent attachment')
ON CONFLICT (component, operator_version, source) DO UPDATE SET
    min_ocp = EXCLUDED.min_ocp,
    max_ocp = EXCLUDED.max_ocp,
    notes = EXCLUDED.notes,
    verified_at = now();

-- =============================================================================
-- 5. Security Advisories, Errata, and Known Bugs (OCP, OCV, Dell CSM, Portworx)
-- =============================================================================
INSERT INTO advisories (source, external_id, title, severity, affected_component, affected_version_range, published_at, url, raw)
VALUES
    ('redhat-cve', 'CVE-2026-21840', 'OpenShift Virtualization vhost-user-blk privilege escalation during VM migration', 'important', 'ocv', '<=4.20.3', '2026-03-01T00:00:00Z', 'https://access.redhat.com/security/cve/CVE-2026-21840', '{"cve": "CVE-2026-21840", "fixed_in": "4.21.0"}'::jsonb),
    ('redhat-cve', 'CVE-2026-44109', 'Kube-apiserver HTTP/2 stream multiplexing DoS in OCP 4.20 control plane', 'moderate', 'ocp', '<=4.20.5', '2026-03-12T00:00:00Z', 'https://access.redhat.com/security/cve/CVE-2026-44109', '{"cve": "CVE-2026-44109", "fixed_in": "4.21.0"}'::jsonb),
    ('redhat-errata', 'RHSA-2026:3310', 'Red Hat OpenShift Virtualization 4.21.0 bug fix and security update', 'important', 'ocv', '4.20.0-4.20.8', '2026-04-10T00:00:00Z', 'https://access.redhat.com/errata/RHSA-2026:3310', '{"errata": "RHSA-2026:3310"}'::jsonb),
    ('redhat-errata', 'RHSA-2026:5520', 'Red Hat OpenShift Container Platform 4.22.8 General Security Advisory', 'moderate', 'ocp', '<4.22.8', '2026-08-01T00:00:00Z', 'https://access.redhat.com/errata/RHSA-2026:5520', '{"errata": "RHSA-2026:5520"}'::jsonb),
    ('dell-csm', 'DELL-CSM-BUG-411', 'PowerStore CSI node pod crashloop on RHEL 9.4 coreos kernel during node reboot', 'important', 'dell-csm', '<=1.13.0', '2026-02-15T00:00:00Z', 'https://dell.github.io/csm-docs/advisories/411', '{"bug": "DELL-CSM-BUG-411", "fixed_in": "1.14.0"}'::jsonb),
    ('portworx', 'PWX-50912', 'Sharedv4 volume mount failure during live migration on OCP 4.21', 'critical', 'portworx', '<=3.1.4', '2026-03-20T00:00:00Z', 'https://docs.portworx.com/release-notes/pwx-50912', '{"bug": "PWX-50912", "fixed_in": "3.2.0"}'::jsonb)
ON CONFLICT (source, external_id) DO UPDATE SET
    title = EXCLUDED.title,
    severity = EXCLUDED.severity,
    affected_version_range = EXCLUDED.affected_version_range,
    raw = EXCLUDED.raw,
    fetched_at = now();

-- =============================================================================
-- 6. Upgrade Graph Edges (Cincinnati / OSUS)
-- Complete upgrade trajectory from 4.20.0 -> 4.21.x -> 4.22.0 .. 4.22.8
-- =============================================================================
INSERT INTO upgrade_edges (channel, arch, from_version, to_version, conditional, risk_name, risk_message, matching_rule)
VALUES
    -- 4.20 z-stream edges
    ('stable-4.20', 'amd64', '4.20.0', '4.20.2', FALSE, NULL, NULL, NULL),
    ('stable-4.20', 'amd64', '4.20.2', '4.20.5', FALSE, NULL, NULL, NULL),
    ('stable-4.20', 'amd64', '4.20.5', '4.20.8', FALSE, NULL, NULL, NULL),
    ('fast-4.20',   'amd64', '4.20.0', '4.20.8', FALSE, NULL, NULL, NULL),
    
    -- 4.20 -> 4.21 Minor Upgrade Boundary (EUS/Standard transition)
    ('stable-4.21', 'amd64', '4.20.8', '4.21.0', FALSE, NULL, NULL, NULL),
    ('fast-4.21',   'amd64', '4.20.0', '4.21.0', TRUE, 'EUSJumpValidation', 'Direct upgrade from 4.20.0 to 4.21.0 requires latest 4.20 z-stream patch', '[{"type": "PromQL", "promql": "cluster_version{version=~\"4.20.[0-4]\"}"}]'::jsonb),
    ('fast-4.21',   'amd64', '4.20.8', '4.21.0', FALSE, NULL, NULL, NULL),
    
    -- 4.21 z-stream progression
    ('stable-4.21', 'amd64', '4.21.0', '4.21.2', FALSE, NULL, NULL, NULL),
    ('stable-4.21', 'amd64', '4.21.2', '4.21.6', FALSE, NULL, NULL, NULL),
    ('stable-4.21', 'amd64', '4.21.6', '4.21.10', FALSE, NULL, NULL, NULL),
    ('stable-4.21', 'amd64', '4.21.10', '4.21.14', FALSE, NULL, NULL, NULL),
    ('fast-4.21',   'amd64', '4.21.0', '4.21.14', FALSE, NULL, NULL, NULL),
    
    -- 4.21 -> 4.22 Minor Upgrade Boundary
    ('stable-4.22', 'amd64', '4.21.14', '4.22.0', FALSE, NULL, NULL, NULL),
    ('fast-4.22',   'amd64', '4.21.10', '4.22.0', TRUE, 'OperatorPrerequisiteCheck', 'Verify OCV, Portworx and Dell CSM operators are upgraded to 4.22-compatible versions before applying 4.22.0 payload', '[{"type": "Always"}]'::jsonb),
    ('fast-4.22',   'amd64', '4.21.14', '4.22.0', FALSE, NULL, NULL, NULL),
    
    -- 4.22 z-stream up to 4.22.8
    ('stable-4.22', 'amd64', '4.22.0', '4.22.2', FALSE, NULL, NULL, NULL),
    ('stable-4.22', 'amd64', '4.22.2', '4.22.4', FALSE, NULL, NULL, NULL),
    ('stable-4.22', 'amd64', '4.22.4', '4.22.6', FALSE, NULL, NULL, NULL),
    ('stable-4.22', 'amd64', '4.22.6', '4.22.8', FALSE, NULL, NULL, NULL),
    ('fast-4.22',   'amd64', '4.22.0', '4.22.8', FALSE, NULL, NULL, NULL),
    ('candidate-4.22', 'amd64', '4.22.4', '4.22.8', FALSE, NULL, NULL, NULL)
ON CONFLICT (channel, arch, from_version, to_version, risk_name) DO UPDATE SET
    conditional = EXCLUDED.conditional,
    risk_message = EXCLUDED.risk_message,
    matching_rule = EXCLUDED.matching_rule,
    fetched_at = now();

-- =============================================================================
-- 7. Release Images Inventory (4.20.0, 4.21.0, 4.21.14, 4.22.0, 4.22.8)
-- =============================================================================
INSERT INTO release_images (component, version, image)
VALUES
    ('ocp', '4.20.0', 'quay.io/openshift-release-dev/ocp-release:4.20.0-x86_64'),
    ('ocp', '4.20.8', 'quay.io/openshift-release-dev/ocp-release:4.20.8-x86_64'),
    ('ocp', '4.21.0', 'quay.io/openshift-release-dev/ocp-release:4.21.0-x86_64'),
    ('ocp', '4.21.14', 'quay.io/openshift-release-dev/ocp-release:4.21.14-x86_64'),
    ('ocp', '4.22.0', 'quay.io/openshift-release-dev/ocp-release:4.22.0-x86_64'),
    ('ocp', '4.22.8', 'quay.io/openshift-release-dev/ocp-release:4.22.8-x86_64'),
    ('ocv', '4.20.0', 'quay.io/openshift-virtualization/virt-operator:v4.20.0'),
    ('ocv', '4.21.0', 'quay.io/openshift-virtualization/virt-operator:v4.21.0'),
    ('ocv', '4.22.0', 'quay.io/openshift-virtualization/virt-operator:v4.22.0'),
    ('ocv', '4.22.8', 'quay.io/openshift-virtualization/virt-operator:v4.22.8')
ON CONFLICT (version, component) DO UPDATE SET
    image = EXCLUDED.image,
    fetched_at = now();

COMMIT;
