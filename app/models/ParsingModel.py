from pydantic import BaseModel
from ..interfaces.ListingService import ListingService
from .TagModel import TagModel

class ParsingModel(BaseModel):
    # Search results parsing fields:
    targetTag: TagModel = TagModel()
    tagMap: list[TagModel] | None = None
    relativeHref: bool = True
    urlAttr: str = 'href'

    requiresTagMap: bool

    # Listing page parsing dict:
    listingService: ListingService

    class Config:
        arbitrary_types_allowed = True