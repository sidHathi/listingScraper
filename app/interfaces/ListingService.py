from abc import ABC, abstractmethod
import re
from typing import Any
from geopy.location import Location

from ..models.Listing import Listing
from ..enums import ListingField, LeaseTerm
from ..constants import listingMap, termToMonthMap, keywordMap
from ..models.TagModel import TagModel
from ..utils.scrapingUtils import findPrice, encodeLocation, findIntegerListMonths, matchLeaseTermByKeyword

class ListingService(ABC):
    @abstractmethod
    def getProviderName(self) -> str:
        ...

    @abstractmethod
    def getOnSuccessTag(self) -> TagModel:
        ...

    @abstractmethod
    def parseName(self, nameStr: str) -> str:
        return nameStr

    @abstractmethod
    def parseLocation(self, locStr: str, queryVal: Any | None = None) -> Location:
        location: Location | None = encodeLocation(locStr)
        if location is None:
            assert queryVal is not None
            return queryVal
        return location

    @abstractmethod
    def parseBedroomOptions(self, opts: str, queryVal: Any | None = None) -> list[int]:
        print(opts)
        studioMatches: list[str] = re.findall(r'(studio)', opts, re.IGNORECASE)
        if len(studioMatches) > 0:
            return [0, 0] # must be 'Studio'
        
        bedsRegexMatch = re.search(r'([-–\d\s]+(beds|bed|bd))', opts, re.I)
        if bedsRegexMatch is None:
            return [0, 0]
        bedsStr: str = re.sub(r'[^0-9-–]', '', bedsRegexMatch.group())
        if len(bedsStr) < 1:
            assert(queryVal is not None)
            return [int(queryVal), int(queryVal)]
        splitVal = re.split(r'[-–]', bedsStr)
        lower = splitVal[0]
        if len(splitVal) == 1:
            return [int(lower), int(lower)]
        upper = splitVal[1]
        return [int(lower), int(upper)]
    
    @abstractmethod
    def parsePrice(self, price: str, queryVal: Any | None = None) -> int:
        print("[PRICE]: " +price);
        numeric = findPrice(price)
        print(numeric)
        if numeric is None or numeric == '':
            return -1

        return int(numeric)
    
    @abstractmethod
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

    @abstractmethod
    def getFieldMaps(self) -> dict[ListingField, list[TagModel] | None]:
        ...

    @abstractmethod
    def getSpecialFieldName(self, field: ListingField) -> str | None:
        ...

    def getFieldValue(self, listing: Listing, field: ListingField) -> Any:
        return listing.dict()[listingMap[field]]

    def parse(self, field: ListingField, val: str, queryVal: Any | None = None) -> Any:
        match(field):
            case ListingField.Name:
                return self.parseName(val)
            case ListingField.Location:
                return self.parseLocation(val, queryVal)
            case ListingField.Bedrooms:
                return self.parseBedroomOptions(val, queryVal)
            case ListingField.Price:
                return self.parsePrice(val, queryVal)
            case ListingField.ShortestLease:
                return self.parseShortestLease(val, queryVal)
            case _:
                return None
    