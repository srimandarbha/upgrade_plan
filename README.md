# OCV upgrade agent — schema + collectors (milestone 1)

Data layer for a disconnected OpenShift Virtualization (OCV) fleet upgrade
agent: pulls Red Hat + vendor advisory/compatibility/upgrade-graph data and
live per-cluster state into one DB. The compatibility engine (GO / NO-GO
logic) and the GitOps PR / alerting pieces are follow-on milestones that read
from this same schema — see `assessments` and `alerts` in `db/schema.sql`,
currently empty.

## Layout

```
db/
  schema.sql        Postgres DDL (source of truth for prod)
  models.py         SQLAlchemy models (same shape, portable to SQLite for dev)
  db.py             engine/session factory, reads $DATABASE_URL
collectors/
  redhat_security.py  CVE + CSAF/errata  -> advisories
  lifecycle.py         GA/EOL dates       -> product_lifecycle
  cincinnati.py         upgrade graph + conditional risks -> upgrade_edges
  cluster_state.py      live ClusterVersion + installed operator CSVs -> component_versions
  vendor_matrix.py      curated Dell CSM / Portworx data  -> operator_compat, advisories
  release_info.py       `oc adm release info` image inventory -> release_images
data/
  vendor_matrix_seed.yaml   hand-maintained, PR-reviewed like any config change
run_collectors.py    orchestrator / CronJob entry point
tests/                unit tests against saved fixtures (no live network needed)
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit DATABASE_URL / CINCINNATI_URL / KUBECONFIG
python run_collectors.py --only redhat-security,lifecycle,cincinnati
```

`init_db()` creates tables automatically against `DATABASE_URL` if they don't
exist yet (`db/schema.sql` is there for DBA review / migration-tool import,
not as a separate manual step).

## Bastion vs. disconnected split

Not every collector can run from the same place:

| Collector | Needs | Run from |
|---|---|---|
| `redhat_security` | internet egress to access.redhat.com | bastion |
| `lifecycle` | internet egress to access.redhat.com | bastion |
| `cincinnati` | internet egress (public) *or* your local OSUS | either — point `CINCINNATI_URL` at OSUS to run disconnected |
| `vendor_matrix` | nothing — reads the checked-in YAML | either |
| `cluster_state` | cluster API access (kubeconfig) | disconnected, where the clusters are |
| `release_info` | `oc` + access to your mirrored release payloads | disconnected |

Run the bastion-only collectors on a schedule there, then ship the resulting
rows across the air gap the same way you already move everything else —
`pg_dump`/`pg_restore` a schema-only slice, or export changed rows as JSON and
push them as an OCI artifact through your existing mirror registry pipeline.
Everything else runs where the clusters and mirrors actually live.

## What each requirement maps to

- **"fetch all data and CVE and security bugs info"** → `redhat_security.py`
  (Red Hat CVE/errata) + `vendor_matrix.py` (Dell/Portworx don't have an API
  for this, so it's a reviewed YAML feeding the same `advisories` table).
- **"alert if due to a specific known bug"** → every advisory lands in
  `advisories` with `affected_component` + `affected_version_range` populated;
  the alerting engine (next milestone) diffs new rows against
  `component_versions` and writes to `alerts`.
- **"whether the version and operators are compatible for upgrade"** →
  `cluster_state.py` reads the live, already-evaluated
  `ClusterVersion.status.conditionalUpdates` instead of re-deriving risk;
  `operator_compat` (from OLM catalog metadata you can add a small
  `opm render`-based loader for, plus `vendor_matrix.py`) covers the operator
  side.
- **cluster/version inventory in your DB** → `clusters` here is a stub;
  point `component_versions.cluster_id` at your real table's primary key
  instead of running this one in production.

## Tests

```bash
pytest
```

Runs entirely against saved fixtures in `tests/fixtures/` — no live network
calls, since this project can't reach access.redhat.com, docs.portworx.com,
or a real cluster from wherever you're reading this. Fixtures mirror the
documented/observed response shapes as closely as possible; the first time
you point a collector at a live endpoint, it's worth diffing one real
response against its fixture in case a vendor has renamed a field since.

## Next milestones

1. **Compatibility engine** — `engine/compatibility.py`: per cluster × candidate
   target, join `component_versions` + `advisories` + `operator_compat` +
   `product_lifecycle` + `upgrade_edges` (+ live conditional-update risks) into
   a GO / GO-WITH-CAVEATS / NO-GO verdict, written to `assessments`.
2. **GitOps PR bot** — on GO, open a PR against your
   `gitops-standards-repo-template`-based repo bumping the relevant
   `targetRevision`, with the assessment as the PR body.
3. **Alerting** — dedup new advisories against the fleet by fingerprint, write
   to `alerts`, notify.
