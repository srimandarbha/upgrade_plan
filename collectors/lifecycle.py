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
    stmt = pg_insert(ProductLifecycle).values(rows)
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
