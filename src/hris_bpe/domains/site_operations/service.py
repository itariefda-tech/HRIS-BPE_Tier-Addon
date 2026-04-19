from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from hris_bpe.common.dependencies import CurrentUserContext
from hris_bpe.common.scope import (
    ensure_company_access,
    filter_items_by_company_scope,
    has_unscoped_permission,
)
from hris_bpe.domains.client_contract.models import Client
from hris_bpe.domains.site_operations.models import ClientSite, SitePost
from hris_bpe.domains.site_operations.repository import SiteOperationsRepository
from hris_bpe.domains.site_operations.schemas import (
    ClientSiteCreateRequest,
    SitePostCreateRequest,
)


class SiteOperationsService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = SiteOperationsRepository(db)

    def list_sites(self, current_user: CurrentUserContext):
        client_company_map = {
            client.id: client.company_id for client in self.db.query(Client).all()
        }
        items = filter_items_by_company_scope(
            current_user,
            self.repository.list_sites(),
            lambda item: client_company_map.get(item.client_id),
        )
        if has_unscoped_permission(current_user, "sites.manage"):
            return items
        if current_user.site_scope_ids:
            items = [item for item in items if item.id in current_user.site_scope_ids]
        return items

    def create_site(self, current_user: CurrentUserContext, payload: ClientSiteCreateRequest):
        client = self.db.get(Client, payload.client_id)
        if client is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client tidak ditemukan.",
            )
        ensure_company_access(
            current_user,
            client.company_id,
            detail="Site tidak berada dalam scope company user.",
        )
        if current_user.branch_scope_ids or current_user.site_scope_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User dengan scope branch/site tidak diizinkan membuat site baru.",
            )
        item = ClientSite(
            **payload.model_dump(),
            created_by=current_user.user.id,
            updated_by=current_user.user.id,
        )
        self.repository.create_site(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list_posts(self, current_user: CurrentUserContext):
        site_client_map = {
            site.id: site.client_id for site in self.repository.list_sites()
        }
        client_company_map = {
            client.id: client.company_id for client in self.db.query(Client).all()
        }
        items = filter_items_by_company_scope(
            current_user,
            self.repository.list_posts(),
            lambda item: client_company_map.get(site_client_map.get(item.client_site_id)),
        )
        if has_unscoped_permission(current_user, "site_posts.manage"):
            return items
        if current_user.site_scope_ids:
            items = [item for item in items if item.client_site_id in current_user.site_scope_ids]
        return items

    def create_post(self, current_user: CurrentUserContext, payload: SitePostCreateRequest):
        site = self.db.get(ClientSite, payload.client_site_id)
        if site is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client site tidak ditemukan.",
            )
        client = self.db.get(Client, site.client_id)
        if client is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client site tidak valid.",
            )
        ensure_company_access(
            current_user,
            client.company_id,
            detail="Site post tidak berada dalam scope company user.",
        )
        if current_user.branch_scope_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User dengan scope branch tidak diizinkan membuat site post.",
            )
        if current_user.site_scope_ids and payload.client_site_id not in current_user.site_scope_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Site post tidak berada dalam scope site user.",
            )
        item = SitePost(
            **payload.model_dump(),
            created_by=current_user.user.id,
            updated_by=current_user.user.id,
        )
        self.repository.create_post(item)
        self.db.commit()
        self.db.refresh(item)
        return item
