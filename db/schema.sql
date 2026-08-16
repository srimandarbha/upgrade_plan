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
