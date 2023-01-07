from typing import Any
from geopy.location import Location
import re

from ..interfaces.ListingService import ListingService
from ..utils.scrapingUtils import matchLeaseTermByKeyword, encodeLocation, findIntegerListMonths
from ..constants import keywordMap, termToMonthMap
from ..enums import ListingField, LeaseTerm
from ..models.TagModel import TagModel

class ZillowListingService(ListingService):
    def __init__(self):
        self.geocodedLocation: Location | None = None

    def getProviderName(self) -> str:
        return 'zillow'

    def getOnSuccessTag(self) -> TagModel:
        return TagModel(tagType='span', identifiers={'data-testid':'price'})

    def parseName(self, nameStr: str) -> str:
        # expects address in nameStr
        if self.geocodedLocation is None:
            self.geocodedLocation = encodeLocation(nameStr)
            if self.geocodedLocation is None:
                return nameStr
        
        locDict = self.geocodedLocation.raw
        assert 'address_components' in locDict and len(locDict['address_components']) > 0 and 'short_name' in locDict['address_components'][0]
        shortLocName = locDict['address_components'][0]['short_name']
        return f'Zillow Rental #{shortLocName}'

    def parseLocation(self, locStr: str, queryVal: Any | None = None) -> Location:
        location: Location | None = self.geocodedLocation or encodeLocation(locStr)
        if location is None:
            assert queryVal is not None
            return queryVal
        return location

    def parseBedroomOptions(self, opts: str, queryVal: Any | None = None) -> list[int]:
        '''
        format {range/number bd OR Studio}
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
        return super().parsePrice(price, queryVal)

    def parseShortestLease(self, lease: str, queryVal: Any | None = None) -> int:
        return super().parseShortestLease(lease, queryVal)

    def getFieldMaps(self) -> dict[ListingField, list[TagModel] | None]:
        return {
            ListingField.Url: None,
            ListingField.Name: [
                TagModel(tagType='h1', identifiers={
                    'class': 'Text-c11n-8-73-0__sc-aiai24-0 kHeRng'
                }),
            ],
            ListingField.Location: [
                TagModel(tagType='h1', identifiers={
                    'class': 'Text-c11n-8-73-0__sc-aiai24-0 kHeRng'
                }),
            ],
            ListingField.REType: None, # use query val
            ListingField.REType: None, # use query val
            ListingField.Bedrooms: [
                TagModel(tagType='span', identifiers={
                    'data-testid': 'bed-bath-item'
                })
            ],
            ListingField.Price: [
                TagModel(tagType='span', identifiers={
                    'data-testid': 'price'
                })
            ],
            ListingField.ShortestLease: [
                TagModel(tagType='div', identifiers={
                    'class': 'ds-overview'
                })
            ],
            ListingField.Pets: None, # use query val
            ListingField.Transit: None # use query val
        }

    def getSpecialFieldName(self, field: ListingField) -> str | None:
        return None
        