from __future__ import annotations

from sqlalchemy.orm import Session

from hris_bpe.domains.product_control.repository import ProductControlRepository


class ProductControlService:
    def __init__(self, db: Session) -> None:
        self.repository = ProductControlRepository(db)

    def list_tiers(self):
        return self.repository.list_tiers()

    def list_feature_modules(self):
        return self.repository.list_feature_modules()

    def list_subscriptions(self):
        return self.repository.list_subscriptions()

