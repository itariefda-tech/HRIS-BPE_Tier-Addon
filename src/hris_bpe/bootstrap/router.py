from fastapi import APIRouter

from hris_bpe.config.settings import get_settings
from hris_bpe.domains.access_control.routes import router as access_control_router
from hris_bpe.domains.attendance.routes import router as attendance_router
from hris_bpe.domains.auth.routes import router as auth_router
from hris_bpe.domains.client_contract.routes import router as client_contract_router
from hris_bpe.domains.dashboard.routes import router as dashboard_router
from hris_bpe.domains.master_hr.routes import router as master_hr_router
from hris_bpe.domains.organization.routes import router as organization_router
from hris_bpe.domains.product_control.routes import router as product_control_router
from hris_bpe.domains.site_operations.routes import router as site_operations_router
from hris_bpe.domains.workforce_operations.routes import (
    my_router as my_workforce_router,
    router as workforce_operations_router,
)


settings = get_settings()
api_router = APIRouter(prefix=settings.api_v1_prefix)

api_router.include_router(auth_router)
api_router.include_router(product_control_router)
api_router.include_router(access_control_router)
api_router.include_router(organization_router)
api_router.include_router(master_hr_router)
api_router.include_router(client_contract_router)
api_router.include_router(site_operations_router)
api_router.include_router(workforce_operations_router)
api_router.include_router(my_workforce_router)
api_router.include_router(attendance_router)
api_router.include_router(dashboard_router)
