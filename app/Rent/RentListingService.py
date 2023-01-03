from typing import Any, cast
from geopy.location import Location
from geopy.exc import GeocoderTimedOut, GeocoderParseError, GeocoderServiceError, GeocoderUnavailable
import re

from ..interfaces.ListingService import ListingService
from ..utils.scrapingUtils import findIntegerListMonths, matchLeaseTermByKeyword, encodeLocation
from ..constants import keywordMap, termToMonthMap
from ..enums import ListingField, LeaseTerm
from ..models.TagModel import TagModel

class RentListingService(ListingService):
    def getProviderName(self) -> str:
        return "rent.com"

    def getOnSuccessTag(self) -> TagModel:
        return TagModel(tagType='h1', identifiers={'data-tid':'property-title'})

    def parseName(self, nameStr: str) -> str:
        return nameStr

    def parseLocation(self, locStr: str, queryVal: Any | None = None) -> Location:
        location: Location | None = encodeLocation(locStr)
        if location is None:
            assert queryVal is not None
            return queryVal
        return location

    def parseBedroomOptions(self, opts: str, queryVal: Any | None = None) -> list[int]:
        '''
        format {range Bed/Beds OR Studio}
        '''
        splitOpts = opts.split(' ')
        if len(splitOpts) < 2:
            return [0, 0] # must be 'Studio'
        
        valStr: str = splitOpts[0]
        splitVal = re.split(r'[-–]', valStr)
        lower = re.sub(r'(studio)', '0', splitVal[0], flags=re.IGNORECASE)
        if len(splitVal) == 1:
            return [int(lower), int(lower)]
        upper = re.sub(r'(studio)', '0', splitVal[1], flags=re.IGNORECASE)
        return [int(lower), int(upper)]

    def parsePrice(self, price: str, queryVal: Any | None = None) -> int:
        numeric = re.sub(r'[^0-9]', '', price)
        if len(numeric) == 0:
            return -1
        return int(numeric)

    def parseShortestLease(self, lease: str, queryVal: Any | None = None) -> int:
        listMatches = findIntegerListMonths(lease)
        if listMatches is not None and len(listMatches) > 0:
            return min(listMatches)
        elif queryVal is not None:
            return int(queryVal)
        elif len(matchLeaseTermByKeyword(lease, keywordMap)) > 0:
            val: int | None = termToMonthMap[matchLeaseTermByKeyword(lease, keywordMap)[0]]
            if val is not None:
                return val
        default = termToMonthMap[LeaseTerm.LongTerm]
        assert(default is not None)
        return default

    def getFieldMaps(self) -> dict[ListingField, list[TagModel] | None]:
        return {
            ListingField.Url: None,
            ListingField.Name: [
                TagModel(tagType=None, identifiers={
                    'data-tid': 'property-title'
                })
            ],
            ListingField.Location: [
                TagModel(tagType='div', identifiers={
                    'data-tid': 'pdpKeyInfo_address'
                }),
                TagModel(tagType='button', identifiers={})
            ],
            ListingField.REType: None, # use query val
            ListingField.Bedrooms: [
                TagModel(tagType='li', identifiers={
                    'data-tid': 'pdpKeyInfo_bedText'
                })
            ],
            ListingField.Price: [
                TagModel(tagType='div', identifiers={
                    'data-tid': 'pdpKeyInfo_price'
                })
            ],
            ListingField.ShortestLease: [
                TagModel(tagType='section', identifiers={
                    'data-tag_section': 'leasing_terms'
                })
            ],
            ListingField.Pets: None, # use query val
            ListingField.Transit: None # use query val
        }

    def getSpecialFieldName(self, field: ListingField) -> str | None:
        return None

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 