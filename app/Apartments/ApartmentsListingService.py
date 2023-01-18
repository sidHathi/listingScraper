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
        print(opts)
        studioMatches: list[str] = re.findall(r'((studio))', opts, re.IGNORECASE)
        if len(studioMatches) > 0:
            return [0, 0] # must be 'Studio'
        
        bedsRegexMatch = re.search(r'(\s[-–\d\s]+(bd))', opts, re.IGNORECASE)
        print(bedsRegexMatch)
        if bedsRegexMatch is None:
            return [0, 0]
        bedsStr: str = re.sub(r'[^0-9-–]', '', bedsRegexMatch.group())
        print(bedsStr)
        if len(bedsStr) < 1:
            assert(queryVal is not None)
            return [int(queryVal), int(queryVal)]
        splitVal = re.split(r'[-–]', bedsStr)
        lower = splitVal[0]
        if len(splitVal) == 1:
            return [int(lower), int(lower)]
        upper = splitVal[1]
        return [int(lower), int(upper)]
    
    def parsePrice(self, price: str, queryVal: Any | None = None) -> int:
        return super().parsePrice(price)
    
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
                    'id': 'priceBedBathAreaInfoWrapper'
                })
            ],
            ListingField.Price: [
                TagModel(tagType='ul', identifiers={
                    'class': 'priceBedRangeInfo'
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
    