from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from hris_bpe.common.helpers import utc_now
from hris_bpe.domains.access_control.repository import AccessControlRepository
from hris_bpe.domains.auth.models import AuthRefreshSession, AuthTokenRevocation
from hris_bpe.domains.client_contract.models import Client
from hris_bpe.domains.master_hr.models import Employee
from hris_bpe.domains.organization.models import Branch, Company
from hris_bpe.domains.site_operations.models import ClientSite


class AuthRepository(AccessControlRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def create_refresh_session(self, item: AuthRefreshSession) -> AuthRefreshSession:
        self.db.add(item)
        self.db.flush()
        return item

    def get_company(self, company_id: int) -> Company | None:
        return self.db.get(Company, company_id)

    def get_employee_company_id(self, employee_id: int | None) -> int | None:
        if employee_id is None:
            return None
        employee = self.db.get(Employee, employee_id)
        return employee.company_id if employee is not None else None

    def list_company_ids_for_branch_scope(self, branch_ids: list[int]) -> set[int]:
        if not branch_ids:
            return set()
        statement = select(Branch.company_id).where(Branch.id.in_(branch_ids))
        return set(self.db.execute(statement).scalars())

    def list_company_ids_for_site_scope(self, site_ids: list[int]) -> set[int]:
        if not site_ids:
            return set()
        statement = (
            select(Client.company_id)
            .join(ClientSite, ClientSite.client_id == Client.id)
            .where(ClientSite.id.in_(site_ids))
        )
        return set(self.db.execute(statement).scalars())

    def get_refresh_session_by_session_id(
        self, session_id: str
    ) -> AuthRefreshSession | None:
        return self.db.execute(
            select(AuthRefreshSession).where(AuthRefreshSession.session_id == session_id)
        ).scalar_one_or_none()

    def revoke_refresh_session(
        self, item: AuthRefreshSession, *, reason: str
    ) -> AuthRefreshSession:
        if item.revoked_at is None:
            item.revoked_at = utc_now()
        item.revoked_reason = reason
        item.last_used_at = utc_now()
        self.db.flush()
        return item

    def rotate_refresh_session(
        self,
        item: AuthRefreshSession,
        *,
        refresh_token_jti: str,
        refresh_token_hash: str,
        expires_at,
    ) -> AuthRefreshSession:
        item.refresh_token_jti = refresh_token_jti
        item.refresh_token_hash = refresh_token_hash
        item.expires_at = expires_at
        item.last_used_at = utc_now()
        self.db.flush()
        return item

    def get_token_revocation(self, token_jti: str) -> AuthTokenRevocation | None:
        return self.db.execute(
            select(AuthTokenRevocation).where(AuthTokenRevocation.token_jti == token_jti)
        ).scalar_one_or_none()

    def is_token_revoked(self, token_jti: str) -> bool:
        return self.get_token_revocation(token_jti) is not None

    def record_token_revocation(
        self,
        *,
        user_id: int,
        token_jti: str,
        token_type: str,
        expires_at,
        session_id: str | None = None,
        reason: str | None = None,
    ) -> AuthTokenRevocation:
        existing = self.get_token_revocation(token_jti)
        if existing is not None:
            return existing
        item = AuthTokenRevocation(
            user_id=user_id,
            session_id=session_id,
            token_jti=token_jti,
            token_type=token_type,
            expires_at=expires_at,
            revoked_at=utc_now(),
            reason=reason,
        )
        self.db.add(item)
        self.db.flush()
        return item
