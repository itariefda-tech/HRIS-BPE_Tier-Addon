from fastapi import APIRouter, Depends

from hris_bpe.common.dependencies import DbSession, require_permissions
from hris_bpe.common.responses import success_payload
from hris_bpe.domains.dashboard.service import DashboardService


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/ops-summary")
def ops_summary(
    db: DbSession,
    current_user=Depends(require_permissions("dashboard.read")),
):
    service = DashboardService(db)
    return success_payload("Ringkasan operasional berhasil diambil.", data=service.ops_summary(current_user))
