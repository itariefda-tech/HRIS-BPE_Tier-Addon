from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from hris_bpe.database.base import (
    AuditActorMixin,
    Base,
    PrimaryKeyMixin,
    TimestampMixin,
    VersionedMixin,
)


class ClientSite(Base, PrimaryKeyMixin, TimestampMixin, AuditActorMixin, VersionedMixin):
    __tablename__ = "client_sites"
    __table_args__ = (
        UniqueConstraint("client_id", "code"),
        Index("ix_client_sites_client_status", "client_id", "status"),
    )

    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), index=True)
    code: Mapped[str] = mapped_column(String(80))
    name: Mapped[str] = mapped_column(String(180))
    address: Mapped[str | None] = mapped_column(Text(), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    province: Mapped[str | None] = mapped_column(String(100), nullable=True)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 6), nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 6), nullable=True)
    radius_meters: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="ACTIVE")


class SitePost(Base, PrimaryKeyMixin, TimestampMixin, AuditActorMixin, VersionedMixin):
    __tablename__ = "site_posts"
    __table_args__ = (
        UniqueConstraint("client_site_id", "code"),
        Index("ix_site_posts_site_active", "client_site_id", "active_flag"),
    )

    client_site_id: Mapped[int] = mapped_column(ForeignKey("client_sites.id"), index=True)
    code: Mapped[str] = mapped_column(String(80))
    name: Mapped[str] = mapped_column(String(180))
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    active_flag: Mapped[bool] = mapped_column(Boolean, default=True)
