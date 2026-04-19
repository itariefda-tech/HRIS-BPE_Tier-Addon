from fastapi import APIRouter, Depends

from hris_bpe.common.dependencies import DbSession, require_permissions
from hris_bpe.common.responses import success_payload
from hris_bpe.domains.product_control.schemas import (
    CompanySubscriptionRead,
    FeatureModuleRead,
    ProductTierRead,
)
from hris_bpe.domains.product_control.service import ProductControlService


router = APIRouter(prefix="/product-control", tags=["product-control"])


@router.get("/tiers")
def list_tiers(
    db: DbSession,
    current_user=Depends(require_permissions("product_control.read")),
):
    service = ProductControlService(db)
    items = [ProductTierRead.model_validate(item).model_dump(mode="json") for item in service.list_tiers()]
    return success_payload("Daftar product tier berhasil diambil.", data=items, meta={"total": len(items)})


@router.get("/feature-modules")
def list_feature_modules(
    db: DbSession,
    current_user=Depends(require_permissions("product_control.read")),
):
    service = ProductControlService(db)
    items = [
        FeatureModuleRead.model_validate(item).model_dump(mode="json")
        for item in service.list_feature_modules()
    ]
    return success_payload("Daftar feature module berhasil diambil.", data=items, meta={"total": len(items)})


@router.get("/subscriptions")
def list_subscriptions(
    db: DbSession,
    current_user=Depends(require_permissions("product_control.read")),
):
    service = ProductControlService(db)
    items = [
        CompanySubscriptionRead.model_validate(item).model_dump(mode="json")
        for item in service.list_subscriptions()
    ]
    return success_payload("Daftar subscription berhasil diambil.", data=items, meta={"total": len(items)})
