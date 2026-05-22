from __future__ import annotations

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
import os

# Module-level singletons — initialized once on first use.
_engine: Engine | None = None
_SessionLocal: sessionmaker | None = None  # type: ignore[type-arg]


def get_engine() -> Engine:
    """Return the shared SQLAlchemy engine, creating it on first call."""
    global _engine
    if _engine is None:
        url = os.getenv("DATABASE_URL", "sqlite:///./data/olist.db")
        if url.startswith("sqlite"):
            _engine = create_engine(
                url,
                connect_args={"check_same_thread": False},
                poolclass=NullPool,
            )
        else:
            _engine = create_engine(url)
    return _engine


def get_session() -> Session:
    """Return a new Session bound to the shared engine.

    The returned Session supports the context-manager protocol so callers
    can write ``with get_session() as session:`` to guarantee cleanup::

        with get_session() as session:
            session.add(obj)
            session.commit()
    """
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=get_engine()
        )
    return _SessionLocal()
