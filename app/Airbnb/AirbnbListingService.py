import re
from typing import Any
from geopy.location import Location

from ..enums import ListingField
from ..interfaces.ListingService import ListingService
from ..models.TagModel import TagModel
from ..utils.scrapingUtils import encodeLocation, extractShortestLeaseFromDescription, findPrice, findCompleteAddress, findCityStatePair

class AirbnbListingService(ListingService):
    def getProviderName(self) -> str:
        return 'airbnb'
    
    def getOnSuccessTag(self) -> TagModel:
        return TagModel(tagType='div', identifiers={'data-section-id': 'OVERVIEW_DEFAULT'})
    
    def parseName(self, nameStr: str) -> str:
        return super().parseName(nameStr)
    
    def parseLocation(self, locStr: str, queryVal: Any | None = None) -> Location:
        addr = findCompleteAddress(locStr)
        if addr is None:
            addr = findCityStatePair(locStr)
        if addr is None:
            assert queryVal is not None
            return queryVal

        return super().parseLocation(locStr=addr, queryVal=queryVal)
    
    def parseBedroomOptions(self, opts: str, queryVal: Any | None = None) -> list[int]:
        return super().parseBedroomOptions(opts, queryVal)
    
    def parsePrice(self, price: str, queryVal: Any | None = None) -> int:
        return super().parsePrice(price, queryVal)
    
    def parseShortestLease(self, lease: str, queryVal: Any | None = None) -> int:
        return super().parseShortestLease(lease, queryVal)
    
    def getFieldMaps(self) -> dict[ListingField, list[TagModel] | None]:
        return {
            ListingField.Url: None,
            ListingField.Name: [
                TagModel(tagType='div', identifiers={
                    'data-section-id': 'TITLE_DEFAULT'
                }),
                TagModel(tagType='h1', identifiers={})
            ],
            ListingField.Location: [
                TagModel(tagType='div', identifiers={
                    'data-section-id': 'TITLE_DEFAULT'
                }),
                TagModel(tagType='button', identifiers={}),
                TagModel(tagType='span', identifiers={}),
            ],
            ListingField.REType: None,
            ListingField.Bedrooms: [
                TagModel(tagType='div', identifiers={
                    'data-section-id': 'OVERVIEW_DEFAULT'
                }),
                TagModel(tagType='ol', identifiers={})
            ],
            ListingField.Price: [
                TagModel(tagType='div', identifiers={
                    'data-section-id': 'BOOK_IT_SIDEBAR'
                }),
                TagModel(tagType='span', identifiers={
                    'class': 'a8jt5op dir dir-ltr'
                }),
            ],
            ListingField.ShortestLease: None, # use queryVal
            ListingField.Pets: None,
            ListingField.Transit: None,
        }

    def getSpecialFieldName(self, field: ListingField) -> str | None:
        return None