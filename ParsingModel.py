from pydantic import BaseModel
from Listing import ListingField
from ListingService import ListingService
from TagModel import TagModel

class ParsingModel(BaseModel):
    '''
    TO-DO: Implement as per https://sidhathi.notion.site/Scraper-Planning-0fc4a6229b534d87b0e0241fd7d27905
    '''
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