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
