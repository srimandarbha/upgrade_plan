import os
import sys
from pathlib import Path

import pytest
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import db.db as db_module  # noqa: E402
from db.models import Base


@pytest.fixture()
def db_session(monkeypatch):
    """A fresh PostgreSQL-backed session per test, wired up as the module-level
    default so collector `collect()` functions (which call get_session()
    internally) transparently use the same test DB."""
    db_url = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/ocv_agent",
    )
    monkeypatch.setenv("DATABASE_URL", db_url)
    db_module._engine = None
    db_module._SessionLocal = None
    engine = db_module.init_db(db_url, create_tables=True)

    # Clean tables before test run to ensure test isolation
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(text(f"TRUNCATE TABLE {table.name} RESTART IDENTITY CASCADE"))

    with db_module.get_session() as session:
        yield session

    # Clean tables after test run
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(text(f"TRUNCATE TABLE {table.name} RESTART IDENTITY CASCADE"))

