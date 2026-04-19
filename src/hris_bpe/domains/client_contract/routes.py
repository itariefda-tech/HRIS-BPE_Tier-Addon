from fastapi import APIRouter, Depends

from hris_bpe.common.dependencies import DbSession, require_permissions
from hris_bpe.common.responses import success_payload
from hris_bpe.domains.client_contract.schemas import (
    ClientContractCreateRequest,
    ClientContractRead,
    ClientCreateRequest,
    ClientRead,
)
from hris_bpe.domains.client_contract.service import ClientContractService


router = APIRouter(prefix="/client-contract", tags=["client-contract"])


@router.get("/clients")
def list_clients(
    db: DbSession,
    current_user=Depends(require_permissions("clients.read")),
):
    service = ClientContractService(db)
    items = [
        ClientRead.model_validate(item).model_dump(mode="json")
        for item in service.list_clients(current_user)
    ]
    return success_payload("Daftar client berhasil diambil.", data=items, meta={"total": len(items)})


@router.post("/clients")
def create_client(
    payload: ClientCreateRequest,
    db: DbSession,
    current_user=Depends(require_permissions("clients.manage")),
):
    service = ClientContractService(db)
    item = service.create_client(current_user, payload)
    return success_payload("Client berhasil dibuat.", data=ClientRead.model_validate(item).model_dump(mode="json"))


@router.get("/contracts")
def list_contracts(
    db: DbSession,
    current_user=Depends(require_permissions("client_contracts.read")),
):
    service = ClientContractService(db)
    items = [
        ClientContractRead.model_validate(item).model_dump(mode="json")
        for item in service.list_contracts(current_user)
    ]
    return success_payload("Daftar contract berhasil diambil.", data=items, meta={"total": len(items)})


@router.post("/contracts")
def create_contract(
    payload: ClientContractCreateRequest,
    db: DbSession,
    current_user=Depends(require_permissions("client_contracts.manage")),
):
    service = ClientContractService(db)
    item = service.create_contract(current_user, payload)
    return success_payload("Client contract berhasil dibuat.", data=ClientContractRead.model_validate(item).model_dump(mode="json"))
