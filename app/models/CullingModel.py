from pydantic import BaseModel
from .TagModel import TagModel

class CullingModel(BaseModel):
    targetField: str | None = None
    targetVal: str
    tagMap: list[TagModel]
    notFoundTag: TagModel | None = None
    expirationTimeInDays: int