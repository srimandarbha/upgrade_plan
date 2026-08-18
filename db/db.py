"""Engine/session management for PostgreSQL.

DATABASE_URL example:
    postgresql+psycopg2://postgres:postgres@localhost:5432/ocv_agent
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from db.models import Base

DEFAULT_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/ocv_agent"


def _load_env_file():
    """Load key=value pairs from .env if present without requiring external packages."""
    env_path = os.path.join(os.getcwd(), ".env")
    if not os.path.exists(env_path):
        return
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k and k not in os.environ:
                    os.environ[k] = v
    except OSError:
        pass


_load_env_file()


def make_engine(url: str | None = None):
    url = url or os.environ.get("DATABASE_URL", DEFAULT_URL)
    return create_engine(url, future=True)


_engine = None
_SessionLocal = None


def init_db(url: str | None = None, create_tables: bool = True):
    """Call once at startup (or let get_session() do it lazily)."""
    global _engine, _SessionLocal
    _engine = make_engine(url)
    _SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False, future=True)
    if create_tables:
        Base.metadata.create_all(_engine)
    return _engine


@contextmanager
def get_session() -> Iterator[Session]:
    global _SessionLocal
    if _SessionLocal is None:
        init_db()
    session = _SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

