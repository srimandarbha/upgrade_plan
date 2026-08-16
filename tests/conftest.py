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
