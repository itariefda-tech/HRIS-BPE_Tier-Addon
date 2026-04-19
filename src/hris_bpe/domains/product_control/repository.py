from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from hris_bpe.domains.product_control.models import (
    CompanySubscription,
    FeatureModule,
    ProductTier,
)


class ProductControlRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_tiers(self) -> list[ProductTier]:
        return list(
            self.db.execute(select(ProductTier).order_by(ProductTier.sort_order)).scalars()
        )

    def list_feature_modules(self) -> list[FeatureModule]:
        return list(
            self.db.execute(select(FeatureModule).order_by(FeatureModule.code)).scalars()
        )

    def list_subscriptions(self) -> list[CompanySubscription]:
        return list(
            self.db.execute(
                select(CompanySubscription).order_by(CompanySubscription.company_id)
            ).scalars()
        )

