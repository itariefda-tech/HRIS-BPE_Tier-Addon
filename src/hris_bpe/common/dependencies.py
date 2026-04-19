from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from hris_bpe.common.security import claim_to_datetime, decode_access_token
from hris_bpe.database.session import get_db_session
from hris_bpe.domains.access_control.models import User
from hris_bpe.domains.auth.repository import AuthRepository


bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(slots=True)
class CurrentUserContext:
    user: User
    role_codes: list[str]
    permission_codes: set[str]
    company_ids: set[int]
    company_scope_ids: set[int]
    branch_scope_ids: set[int]
    site_scope_ids: set[int]
    has_explicit_scope: bool
    access_token_jti: str
    access_token_expires_at: datetime
    session_id: str | None


DbSession = Annotated[Session, Depends(get_db_session)]


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db_session),
) -> CurrentUserContext:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token akses dibutuhkan.",
        )

    try:
        payload = decode_access_token(credentials.credentials)
        if payload.get("type") != "access":
            raise ValueError("Token type tidak valid.")
        user_id = int(payload["sub"])
        token_jti = str(payload["jti"])
        token_expires_at = claim_to_datetime(payload, "exp")
        session_id = payload.get("sid")
    except (jwt.InvalidTokenError, KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token akses tidak valid.",
        ) from exc

    repo = AuthRepository(db)
    if repo.is_token_revoked(token_jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token akses sudah direvoke.",
        )

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User tidak aktif atau tidak ditemukan.",
        )

    roles = repo.list_roles_for_user(user.id)
    permissions = repo.list_permissions_for_user(user.id)
    company_ids = {role.company_id for role in roles if role.company_id is not None}
    scopes = repo.list_scopes_for_user(user.id)
    company_scope_ids = {
        scope.company_id for scope in scopes if scope.company_id is not None
    }
    branch_scope_ids = {scope.branch_id for scope in scopes if scope.branch_id is not None}
    site_scope_ids = {
        scope.client_site_id for scope in scopes if scope.client_site_id is not None
    }
    return CurrentUserContext(
        user=user,
        role_codes=[role.code for role in roles],
        permission_codes={permission.code for permission in permissions},
        company_ids=company_ids,
        company_scope_ids=company_scope_ids,
        branch_scope_ids=branch_scope_ids,
        site_scope_ids=site_scope_ids,
        has_explicit_scope=len(scopes) > 0,
        access_token_jti=token_jti,
        access_token_expires_at=token_expires_at,
        session_id=str(session_id) if session_id is not None else None,
    )


CurrentUser = Annotated[CurrentUserContext, Depends(get_current_user)]


def require_permissions(*permission_codes: str):
    def _dependency(
        current_user: CurrentUserContext = Depends(get_current_user),
    ) -> CurrentUserContext:
        missing = [
            code for code in permission_codes if code not in current_user.permission_codes
        ]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Izin tidak cukup: {', '.join(missing)}",
            )
        return current_user

    return _dependency
