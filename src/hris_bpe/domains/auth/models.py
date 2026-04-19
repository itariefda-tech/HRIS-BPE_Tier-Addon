from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from hris_bpe.database.base import Base, PrimaryKeyMixin, TimestampMixin, VersionedMixin


class AuthRefreshSession(Base, PrimaryKeyMixin, TimestampMixin, VersionedMixin):
    __tablename__ = "auth_refresh_sessions"
    __table_args__ = (
        Index("ix_auth_refresh_sessions_user_revoked", "user_id", "revoked_at"),
        Index("ix_auth_refresh_sessions_session_revoked", "session_id", "revoked_at"),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    session_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    refresh_token_jti: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    refresh_token_hash: Mapped[str] = mapped_column(String(128))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    revoked_reason: Mapped[str | None] = mapped_column(String(120), nullable=True)


class AuthTokenRevocation(Base, PrimaryKeyMixin):
    __tablename__ = "auth_token_revocations"
    __table_args__ = (
        Index("ix_auth_token_revocations_user_type", "user_id", "token_type"),
        Index("ix_auth_token_revocations_session_type", "session_id", "token_type"),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    session_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    token_jti: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    token_type: Mapped[str] = mapped_column(String(20), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    revoked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    reason: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
