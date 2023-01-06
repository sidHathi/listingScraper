import re
from typing import Any
from geopy.location import Location

from ..interfaces.ListingService import ListingService
from ..models.TagModel import TagModel
from ..utils.scrapingUtils import encodeLocation, extractShortestLeaseFromDescription
from ..constants import termToMonthMap
from ..enums import LeaseTerm, ListingField

class ApartmentsListingService(ListingService):
    def getProviderName(self) -> str:
        return 'apartments.com'
    
    def getOnSuccessTag(self) -> TagModel:
        return TagModel(tagType='h1', identifiers={'id':'propertyName'})
    
    def parseName(self, nameStr: str) -> str:
        return super().parseName(nameStr)
    
    def parseLocation(self, locStr: str, queryVal: Any | None = None) -> Location:
        return super().parseLocation(locStr, queryVal)
    
    def parseBedroomOptions(self, opts: str, queryVal: Any | None = None) -> list[int]:
        return super().parseBedroomOptions(opts, queryVal)
    
    def parsePrice(self, price: str, queryVal: Any | None = None) -> int:
        range = price.split(' - ')
        lowerBound = range[0]
        numeric = re.sub(r'[^0-9]', '', lowerBound)
        if len(numeric) == 0:
            return -1
        return int(numeric)
    
    def parseShortestLease(self, lease: str, queryVal: Any | None = None) -> int:
        shortestLease: int | None = extractShortestLeaseFromDescription(lease)
        if shortestLease is not None:
            return shortestLease
        elif queryVal is not None:
            return queryVal
        else:
            default = termToMonthMap[LeaseTerm.LongTerm]
            assert(default is not None)
            return default
        
    def getFieldMaps(self) -> dict[ListingField, list[TagModel] | None]:
        return {
            ListingField.Url: None,
            ListingField.Name: [
                TagModel(tagType='h1', identifiers={
                    'id': 'propertyName'
                }),
            ],
            ListingField.Location: [
                TagModel(tagType='div', identifiers={
                    'class': 'propertyName'
                }),
            ],
            ListingField.REType: None, # use query val
            ListingField.REType: None, # use query val
            ListingField.Bedrooms: [
                TagModel(tagType='div', identifiers={
                    'class': 'rentInfoDetail'
                })
            ],
            ListingField.Price: [
                TagModel(tagType='p', identifiers={
                    'class': 'rentInfoDetail'
                })
            ],
            ListingField.ShortestLease: [
                TagModel(tagType='section', identifiers={
                    'id': 'feesSection'
                })
            ],
            ListingField.Pets: None, # use query val
            ListingField.Transit: None # use query val
        }

    def getSpecialFieldName(self, field: ListingField) -> str | None:
        return None
    