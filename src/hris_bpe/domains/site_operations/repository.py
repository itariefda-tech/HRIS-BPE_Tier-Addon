from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from hris_bpe.domains.site_operations.models import ClientSite, SitePost


class SiteOperationsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_sites(self) -> list[ClientSite]:
        return list(self.db.execute(select(ClientSite).order_by(ClientSite.code)).scalars())

    def create_site(self, item: ClientSite) -> ClientSite:
        self.db.add(item)
        self.db.flush()
        return item

    def get_site(self, site_id: int) -> ClientSite | None:
        return self.db.get(ClientSite, site_id)

    def list_posts(self) -> list[SitePost]:
        return list(self.db.execute(select(SitePost).order_by(SitePost.code)).scalars())

    def create_post(self, item: SitePost) -> SitePost:
        self.db.add(item)
        self.db.flush()
        return item

    def get_post(self, post_id: int) -> SitePost | None:
        return self.db.get(SitePost, post_id)
