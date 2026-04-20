from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from hris_bpe.common.dependencies import CurrentUserContext
from hris_bpe.common.scope import ensure_company_access, filter_items_by_company_scope
from hris_bpe.domains.client_contract.models import Client, ClientContract
from hris_bpe.domains.client_contract.repository import ClientContractRepository
from hris_bpe.domains.client_contract.schemas import (
    ClientContractCreateRequest,
    ClientCreateRequest,
    ClientUpdateRequest,
)


class ClientContractService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = ClientContractRepository(db)

    def list_clients(self, current_user: CurrentUserContext):
        return filter_items_by_company_scope(
            current_user,
            self.repository.list_clients(),
            lambda item: item.company_id,
        )

    def _get_accessible_client(
        self, current_user: CurrentUserContext, client_id: int
    ) -> Client:
        client = self.repository.get_client(client_id)
        if client is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client tidak ditemukan.",
            )
        allowed_client_ids = {item.id for item in self.list_clients(current_user)}
        if client.id not in allowed_client_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Client tidak berada dalam scope akses user.",
            )
        return client

    def create_client(self, current_user: CurrentUserContext, payload: ClientCreateRequest):
        ensure_company_access(current_user, payload.company_id, detail="Client tidak berada dalam scope company user.")
        item = Client(
            **payload.model_dump(),
            created_by=current_user.user.id,
            updated_by=current_user.user.id,
        )
        self.repository.create_client(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get_client_detail(
        self, current_user: CurrentUserContext, client_id: int
    ) -> Client:
        return self._get_accessible_client(current_user, client_id)

    def update_client(
        self,
        current_user: CurrentUserContext,
        client_id: int,
        payload: ClientUpdateRequest,
    ) -> Client:
        client = self._get_accessible_client(current_user, client_id)
        changes = payload.model_dump(exclude_unset=True)
        if not changes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payload update client kosong.",
            )
        ensure_company_access(
            current_user,
            client.company_id,
            detail="Client tidak berada dalam scope company user.",
        )
        for field_name, value in changes.items():
            setattr(client, field_name, value)
        client.updated_by = current_user.user.id
        self.db.commit()
        self.db.refresh(client)
        return client

    def list_contracts(self, current_user: CurrentUserContext):
        client_company_map = {
            client.id: client.company_id for client in self.repository.list_clients()
        }
        return filter_items_by_company_scope(
            current_user,
            self.repository.list_contracts(),
            lambda item: client_company_map.get(item.client_id),
        )

    def create_contract(
        self, current_user: CurrentUserContext, payload: ClientContractCreateRequest
    ):
        client = self.db.get(Client, payload.client_id)
        if client is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client tidak ditemukan.",
            )
        ensure_company_access(
            current_user,
            client.company_id,
            detail="Contract tidak berada dalam scope company user.",
        )
        item = ClientContract(
            **payload.model_dump(),
            created_by=current_user.user.id,
            updated_by=current_user.user.id,
        )
        self.repository.create_contract(item)
        self.db.commit()
        self.db.refresh(item)
        return item
