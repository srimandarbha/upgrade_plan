"""SQLAlchemy models mirroring db/schema.sql.

Uses the generic `JSON` type (not Postgres-specific JSONB) so the same models
work against SQLite for local dev/tests and Postgres in production -- see
schema.sql for the JSONB-flavored DDL used for the real deployment.
"""
from __future__ import annotations

import datetime as dt

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def _utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


class Cluster(Base):
    """Minimal stub -- replace with / point at your real cluster inventory table."""

    __tablename__ = "clusters"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    region: Mapped[str] = mapped_column(String)
    env: Mapped[str] = mapped_column(String, default="prod")
    ocp_version: Mapped[str] = mapped_column(String)
    api_url: Mapped[str | None] = mapped_column(String, nullable=True)
    kubeconfig_context: Mapped[str | None] = mapped_column(String, nullable=True)
    connected: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    component_versions: Mapped[list["ComponentVersion"]] = relationship(
        back_populates="cluster", cascade="all, delete-orphan"
    )


class ComponentVersion(Base):
    __tablename__ = "component_versions"
    __table_args__ = (UniqueConstraint("cluster_id", "component"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    cluster_id: Mapped[int] = mapped_column(ForeignKey("clusters.id", ondelete="CASCADE"))
    component: Mapped[str] = mapped_column(String)  # ocp | ocv | dell-csm | portworx | ...
    version: Mapped[str] = mapped_column(String)
    channel: Mapped[str | None] = mapped_column(String, nullable=True)
    namespace: Mapped[str | None] = mapped_column(String, nullable=True)
    csv_name: Mapped[str | None] = mapped_column(String, nullable=True)
    observed_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    cluster: Mapped["Cluster"] = relationship(back_populates="component_versions")


class Advisory(Base):
    __tablename__ = "advisories"
    __table_args__ = (UniqueConstraint("source", "external_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String)  # redhat-cve | redhat-errata | dell-csm | portworx
    external_id: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(Text)
    severity: Mapped[str | None] = mapped_column(String, nullable=True)
    affected_component: Mapped[str | None] = mapped_column(String, nullable=True)
    affected_version_range: Mapped[str | None] = mapped_column(String, nullable=True)
    published_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    url: Mapped[str | None] = mapped_column(String, nullable=True)
    fetched_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    raw: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class OperatorCompat(Base):
    __tablename__ = "operator_compat"
    __table_args__ = (UniqueConstraint("component", "operator_version", "source"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    component: Mapped[str] = mapped_column(String)
    operator_version: Mapped[str] = mapped_column(String)
    min_ocp: Mapped[str | None] = mapped_column(String, nullable=True)
    max_ocp: Mapped[str | None] = mapped_column(String, nullable=True)
    source: Mapped[str] = mapped_column(String)  # olm-catalog | dell-support-matrix | portworx-support-matrix
    verified_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class ProductLifecycle(Base):
    __tablename__ = "product_lifecycle"
    __table_args__ = (UniqueConstraint("component", "version"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    component: Mapped[str] = mapped_column(String)
    version: Mapped[str] = mapped_column(String)
    phase: Mapped[str | None] = mapped_column(String, nullable=True)
    ga_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    full_support_end: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    maintenance_end: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    eol_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    fetched_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class UpgradeEdge(Base):
    __tablename__ = "upgrade_edges"
    __table_args__ = (
        UniqueConstraint("channel", "arch", "from_version", "to_version", "risk_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    channel: Mapped[str] = mapped_column(String)
    arch: Mapped[str] = mapped_column(String, default="amd64")
    from_version: Mapped[str] = mapped_column(String)
    to_version: Mapped[str] = mapped_column(String)
    conditional: Mapped[bool] = mapped_column(Boolean, default=False)
    risk_name: Mapped[str | None] = mapped_column(String, nullable=True)
    risk_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    matching_rule: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    fetched_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class ReleaseImage(Base):
    __tablename__ = "release_images"
    __table_args__ = (UniqueConstraint("version", "component"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    component: Mapped[str] = mapped_column(String)
    version: Mapped[str] = mapped_column(String)
    image: Mapped[str] = mapped_column(String)
    fetched_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class Assessment(Base):
    """Written by the compatibility engine (next milestone)."""

    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(primary_key=True)
    cluster_id: Mapped[int] = mapped_column(ForeignKey("clusters.id", ondelete="CASCADE"))
    target_version: Mapped[str] = mapped_column(String)
    verdict: Mapped[str] = mapped_column(String)  # go | go-with-caveats | no-go
    reasons: Mapped[dict] = mapped_column(JSON)
    evaluated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class Alert(Base):
    """Written by the alerting engine (future milestone)."""

    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    fingerprint: Mapped[str] = mapped_column(String, unique=True)
    cluster_id: Mapped[int | None] = mapped_column(
        ForeignKey("clusters.id", ondelete="CASCADE"), nullable=True
    )
    advisory_id: Mapped[int | None] = mapped_column(
        ForeignKey("advisories.id", ondelete="CASCADE"), nullable=True
    )
    message: Mapped[str] = mapped_column(Text)
    first_seen: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    last_seen: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    acknowledged_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
