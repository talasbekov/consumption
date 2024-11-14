from typing import Optional

from schemas import Model


class RankBase(Model):
    name: Optional[str]


class RankCreate(RankBase):
    pass


class RankUpdate(RankBase):
    pass


class RankRead(RankBase, Model):
    id: int
