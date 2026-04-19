from fastapi import APIRouter, Depends

from hris_bpe.common.dependencies import DbSession, require_permissions
from hris_bpe.common.responses import success_payload
from hris_bpe.domains.site_operations.schemas import (
    ClientSiteCreateRequest,
    ClientSiteRead,
    SitePostCreateRequest,
    SitePostRead,
)
from hris_bpe.domains.site_operations.service import SiteOperationsService


router = APIRouter(prefix="/site-operations", tags=["site-operations"])


@router.get("/sites")
def list_sites(
    db: DbSession,
    current_user=Depends(require_permissions("sites.read")),
):
    service = SiteOperationsService(db)
    items = [
        ClientSiteRead.model_validate(item).model_dump(mode="json")
        for item in service.list_sites(current_user)
    ]
    return success_payload("Daftar site berhasil diambil.", data=items, meta={"total": len(items)})


@router.post("/sites")
def create_site(
    payload: ClientSiteCreateRequest,
    db: DbSession,
    current_user=Depends(require_permissions("sites.manage")),
):
    service = SiteOperationsService(db)
    item = service.create_site(current_user, payload)
    return success_payload("Site berhasil dibuat.", data=ClientSiteRead.model_validate(item).model_dump(mode="json"))


@router.get("/posts")
def list_posts(
    db: DbSession,
    current_user=Depends(require_permissions("site_posts.read")),
):
    service = SiteOperationsService(db)
    items = [
        SitePostRead.model_validate(item).model_dump(mode="json")
        for item in service.list_posts(current_user)
    ]
    return success_payload("Daftar site post berhasil diambil.", data=items, meta={"total": len(items)})


@router.post("/posts")
def create_post(
    payload: SitePostCreateRequest,
    db: DbSession,
    current_user=Depends(require_permissions("site_posts.manage")),
):
    service = SiteOperationsService(db)
    item = service.create_post(current_user, payload)
    return success_payload("Site post berhasil dibuat.", data=SitePostRead.model_validate(item).model_dump(mode="json"))
