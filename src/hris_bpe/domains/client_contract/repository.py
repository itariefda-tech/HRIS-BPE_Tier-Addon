from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from hris_bpe.domains.client_contract.models import Client, ClientContract


class ClientContractRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_clients(self) -> list[Client]:
        return list(self.db.execute(select(Client).order_by(Client.code)).scalars())

    def create_client(self, item: Client) -> Client:
        self.db.add(item)
        self.db.flush()
        return item

    def list_contracts(self) -> list[ClientContract]:
        return list(self.db.execute(select(ClientContract).order_by(ClientContract.contract_number)).scalars())

    def create_contract(self, item: ClientContract) -> ClientContract:
        self.db.add(item)
        self.db.flush()
        return item

