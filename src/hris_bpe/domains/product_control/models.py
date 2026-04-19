from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from hris_bpe.database.base import (
    AuditActorMixin,
    Base,
    PrimaryKeyMixin,
    TimestampMixin,
    VersionedMixin,
)


class ProductTier(Base, PrimaryKeyMixin, TimestampMixin):
    __tablename__ = "product_tiers"

    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class FeatureModule(Base, PrimaryKeyMixin, TimestampMixin):
    __tablename__ = "feature_modules"

    code: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(150))
    module_category: Mapped[str] = mapped_column(String(50))
    default_tier_id: Mapped[int | None] = mapped_column(
        ForeignKey("product_tiers.id"), nullable=True
    )
    is_add_on: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class CompanySubscription(
    Base, PrimaryKeyMixin, TimestampMixin, AuditActorMixin, VersionedMixin
):
    __tablename__ = "company_subscriptions"
    __table_args__ = (
        Index("ix_company_subscriptions_company_status", "company_id", "subscription_status"),
        Index("ix_company_subscriptions_tier_status", "product_tier_id", "subscription_status"),
    )

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    product_tier_id: Mapped[int] = mapped_column(ForeignKey("product_tiers.id"), index=True)
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    subscription_status: Mapped[str] = mapped_column(String(50), default="ACTIVE")
    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)


class CompanyFeatureModule(
    Base, PrimaryKeyMixin, TimestampMixin, AuditActorMixin, VersionedMixin
):
    __tablename__ = "company_feature_modules"
    __table_args__ = (
        Index(
            "ix_company_feature_modules_subscription_active",
            "company_subscription_id",
            "active_flag",
        ),
        Index(
            "ix_company_feature_modules_module_active",
            "feature_module_id",
            "active_flag",
        ),
    )

    company_subscription_id: Mapped[int] = mapped_column(
        ForeignKey("company_subscriptions.id"), index=True
    )
    feature_module_id: Mapped[int] = mapped_column(ForeignKey("feature_modules.id"), index=True)
    activation_type: Mapped[str] = mapped_column(String(50), default="included")
    active_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    activated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expired_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)
