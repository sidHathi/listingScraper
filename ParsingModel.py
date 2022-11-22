from pydantic import BaseModel
from Listing import ListingField

class TagModel(BaseModel):
    tagType: str = 'a'
    identifiers: dict[str, str] = {}

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
    listingFieldMaps: dict[ListingField, list[TagModel]]