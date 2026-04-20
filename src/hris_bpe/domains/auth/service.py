from __future__ import annotations

from typing import get_args
from uuid import uuid4

import jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from hris_bpe.common.dependencies import CurrentUserContext
from hris_bpe.common.security import (
    claim_to_datetime,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    hash_password,
    hash_token,
    verify_password,
    verify_token_hash,
)
from hris_bpe.domains.auth.models import AuthRefreshSession
from hris_bpe.domains.auth.repository import AuthRepository
from hris_bpe.domains.auth.schemas import (
    AuthenticatedUser,
    ChangePasswordRequest,
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    UserPreferenceUpdateRequest,
)


class AuthService:
    SYSTEM_DEFAULT_LANGUAGE = "id"
    SYSTEM_DEFAULT_THEME = "theme_1"
    ALLOWED_LANGUAGES = set(
        get_args(AuthenticatedUser.model_fields["preferred_language"].annotation)
    )
    ALLOWED_THEMES = set(
        get_args(AuthenticatedUser.model_fields["preferred_theme"].annotation)
    )

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = AuthRepository(db)

    def _get_active_user_by_login(self, identifier: str):
        user = self.repository.get_user_by_login(identifier)
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User tidak ditemukan atau tidak aktif.",
            )
        return user

    def _build_authenticated_user(self, user) -> AuthenticatedUser:
        roles = self.repository.list_roles_for_user(user.id)
        permissions = self.repository.list_permissions_for_user(user.id)
        scopes = self.repository.list_scopes_for_user(user.id)
        company_ids = {role.company_id for role in roles if role.company_id is not None}
        company_default_language, company_default_theme = self._resolve_company_defaults(
            user,
            company_ids=company_ids,
            scopes=scopes,
        )
        return AuthenticatedUser(
            id=user.id,
            employee_id=user.employee_id,
            username=user.username,
            email=user.email,
            phone=user.phone,
            preferred_language=self._resolve_preferred_language(
                user,
                company_default_language=company_default_language,
            ),
            preferred_theme=self._resolve_preferred_theme(
                user,
                company_default_theme=company_default_theme,
            ),
            is_active=user.is_active,
            last_login_at=user.last_login_at,
            role_codes=[role.code for role in roles],
            permission_codes=[permission.code for permission in permissions],
            company_ids=sorted(company_ids),
            company_scope_ids=sorted(
                {scope.company_id for scope in scopes if scope.company_id is not None}
            ),
            branch_scope_ids=sorted(
                {scope.branch_id for scope in scopes if scope.branch_id is not None}
            ),
            site_scope_ids=sorted(
                {
                    scope.client_site_id
                    for scope in scopes
                    if scope.client_site_id is not None
                }
            ),
            has_explicit_scope=len(scopes) > 0,
        )

    @classmethod
    def _normalize_preference_value(
        cls,
        value: str | None,
        *,
        allowed_values: set[str],
    ) -> str | None:
        value = (value or "").strip().lower()
        if value in allowed_values:
            return value
        return None

    @classmethod
    def _resolve_preferred_language(
        cls,
        user,
        *,
        company_default_language: str | None,
    ) -> str:
        return (
            cls._normalize_preference_value(
                user.preferred_language,
                allowed_values=cls.ALLOWED_LANGUAGES,
            )
            or company_default_language
            or cls.SYSTEM_DEFAULT_LANGUAGE
        )

    @classmethod
    def _resolve_preferred_theme(
        cls,
        user,
        *,
        company_default_theme: str | None,
    ) -> str:
        return (
            cls._normalize_preference_value(
                user.preferred_theme,
                allowed_values=cls.ALLOWED_THEMES,
            )
            or company_default_theme
            or cls.SYSTEM_DEFAULT_THEME
        )

    def _resolve_company_defaults(
        self,
        user,
        *,
        company_ids: set[int],
        scopes,
    ) -> tuple[str | None, str | None]:
        company = self._resolve_preference_company(
            user,
            company_ids=company_ids,
            scopes=scopes,
        )
        if company is None:
            return None, None
        return (
            self._normalize_preference_value(
                company.default_language,
                allowed_values=self.ALLOWED_LANGUAGES,
            ),
            self._normalize_preference_value(
                company.default_theme,
                allowed_values=self.ALLOWED_THEMES,
            ),
        )

    def _resolve_preference_company(self, user, *, company_ids: set[int], scopes):
        scope_company_ids = {
            scope.company_id for scope in scopes if scope.company_id is not None
        }
        if len(scope_company_ids) == 1:
            return self.repository.get_company(next(iter(scope_company_ids)))

        branch_scope_ids = [
            scope.branch_id for scope in scopes if scope.branch_id is not None
        ]
        branch_company_ids = self.repository.list_company_ids_for_branch_scope(
            branch_scope_ids
        )
        if len(branch_company_ids) == 1:
            return self.repository.get_company(next(iter(branch_company_ids)))

        site_scope_ids = [
            scope.client_site_id for scope in scopes if scope.client_site_id is not None
        ]
        site_company_ids = self.repository.list_company_ids_for_site_scope(site_scope_ids)
        if len(site_company_ids) == 1:
            return self.repository.get_company(next(iter(site_company_ids)))

        employee_company_id = self.repository.get_employee_company_id(user.employee_id)
        if employee_company_id is not None:
            return self.repository.get_company(employee_company_id)

        if not company_ids:
            return None
        return self.repository.get_company(sorted(company_ids)[0])

    @staticmethod
    def _generate_session_id() -> str:
        return uuid4().hex

    def _issue_token_pair(self, user_id: int, *, session_id: str):
        access_token = create_access_token(str(user_id), session_id=session_id)
        refresh_token = create_refresh_token(str(user_id), session_id=session_id)
        return access_token, refresh_token

    def login(self, payload: LoginRequest) -> LoginResponse:
        user = self._get_active_user_by_login(payload.identifier)
        if not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password tidak valid.",
            )

        self.repository.set_last_login(user)
        session_id = self._generate_session_id()
        access_token, refresh_token = self._issue_token_pair(user.id, session_id=session_id)
        self.repository.create_refresh_session(
            AuthRefreshSession(
                user_id=user.id,
                session_id=session_id,
                refresh_token_jti=refresh_token.token_jti,
                refresh_token_hash=hash_token(refresh_token.token),
                expires_at=refresh_token.expires_at,
            )
        )
        self.db.commit()

        return LoginResponse(
            access_token=access_token.token,
            refresh_token=refresh_token.token,
            token_type="bearer",
            session_id=session_id,
            access_token_expires_at=access_token.expires_at,
            refresh_token_expires_at=refresh_token.expires_at,
            user=self._build_authenticated_user(user),
        )

    def me(self, current_user: CurrentUserContext) -> AuthenticatedUser:
        return self._build_authenticated_user(current_user.user)

    def refresh(self, payload: RefreshTokenRequest) -> RefreshTokenResponse:
        try:
            token_payload = decode_access_token(payload.refresh_token)
            if token_payload.get("type") != "refresh":
                raise ValueError("Token type tidak valid.")
            user_id = int(token_payload["sub"])
            refresh_token_jti = str(token_payload["jti"])
            session_id = str(token_payload["sid"])
            claim_to_datetime(token_payload, "exp")
        except (jwt.InvalidTokenError, KeyError, ValueError) as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token tidak valid.",
            ) from exc

        refresh_session = self.repository.get_refresh_session_by_session_id(session_id)
        if refresh_session is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sesi refresh token tidak ditemukan.",
            )
        if refresh_session.revoked_at is not None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token sudah direvoke.",
            )
        if (
            refresh_session.refresh_token_jti != refresh_token_jti
            or not verify_token_hash(payload.refresh_token, refresh_session.refresh_token_hash)
        ):
            self.repository.revoke_refresh_session(
                refresh_session,
                reason="refresh_token_reuse_detected",
            )
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token tidak valid.",
            )

        user = self.repository.get_user(user_id)
        if user is None or not user.is_active:
            self.repository.revoke_refresh_session(
                refresh_session,
                reason="user_not_active",
            )
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User tidak aktif atau tidak ditemukan.",
            )

        access_token, refresh_token = self._issue_token_pair(user.id, session_id=session_id)
        self.repository.rotate_refresh_session(
            refresh_session,
            refresh_token_jti=refresh_token.token_jti,
            refresh_token_hash=hash_token(refresh_token.token),
            expires_at=refresh_token.expires_at,
        )
        self.db.commit()

        return RefreshTokenResponse(
            access_token=access_token.token,
            refresh_token=refresh_token.token,
            token_type="bearer",
            session_id=session_id,
            access_token_expires_at=access_token.expires_at,
            refresh_token_expires_at=refresh_token.expires_at,
            user=self._build_authenticated_user(user),
        )

    def logout(self, current_user: CurrentUserContext) -> LogoutResponse:
        self.repository.record_token_revocation(
            user_id=current_user.user.id,
            token_jti=current_user.access_token_jti,
            token_type="access",
            expires_at=current_user.access_token_expires_at,
            session_id=current_user.session_id,
            reason="logout",
        )
        if current_user.session_id is not None:
            refresh_session = self.repository.get_refresh_session_by_session_id(
                current_user.session_id
            )
            if refresh_session is not None and refresh_session.revoked_at is None:
                self.repository.revoke_refresh_session(
                    refresh_session,
                    reason="logout",
                )
        self.db.commit()
        return LogoutResponse(
            revoked_access_token_jti=current_user.access_token_jti,
            revoked_session_id=current_user.session_id,
        )

    def change_password(
        self, current_user: CurrentUserContext, payload: ChangePasswordRequest
    ) -> AuthenticatedUser:
        if not verify_password(payload.current_password, current_user.user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password saat ini tidak sesuai.",
            )
        current_user.user.password_hash = hash_password(payload.new_password)
        current_user.user.updated_by = current_user.user.id
        self.db.commit()
        self.db.refresh(current_user.user)
        return self.me(current_user)

    def update_preferences(
        self,
        current_user: CurrentUserContext,
        payload: UserPreferenceUpdateRequest,
    ) -> AuthenticatedUser:
        if payload.preferred_language is None and payload.preferred_theme is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimal satu preferensi harus dikirim.",
            )
        if payload.preferred_language is not None:
            current_user.user.preferred_language = payload.preferred_language
        if payload.preferred_theme is not None:
            current_user.user.preferred_theme = payload.preferred_theme
        current_user.user.updated_by = current_user.user.id
        self.db.commit()
        self.db.refresh(current_user.user)
        return self.me(current_user)
