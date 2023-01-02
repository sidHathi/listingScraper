from typing import Any
from geopy.location import Location
import re

from ..enums import QueryParam, REType, LeaseTerm, UrlFieldType
from ..models.Query import Query
from ..interfaces.UrlService import UrlService
from ..utils.scrapingUtils import parseNominatimLocation, parseGMV3Location

class RentUrlService(UrlService):
    def baseUrl(self) -> str:
        return 'https://www.rent.com/'

    def paramSeparator(self) -> str:
        return '_'

    def usesQueryParams(self) -> bool:
        return False

    def location(self, queryLocation: Location) -> list[str]:
        city, state = parseNominatimLocation(queryLocation) or parseGMV3Location(queryLocation) or [None, None]
        if city is None or state is None:
            return []
        return [re.sub(' ', '-', state.lower()), re.sub(' ', '-', city.lower())]
    
    def reType(self, param: REType) -> str:
        match(param):
            case REType.Apartment:
                return 'apartments'
            case REType.House:
                return 'houses'
            case REType.Condo:
                return 'condos'
            case _:
                return 'invalid param'
    
    def bedrooms(self, param: int) -> str | None:
        if param == 0:
            return 'studio'
        elif 1 <= param <= 3:
            return f"{param}-bedroom"
        elif param > 3:
            return '4-bedroom' 
        return None

    def priceRange(self, param: list[int]) -> list[str]:
        # returns [min, max] as strings
        if (len(param) < 2):
            return []
        return ['', f"max-price-{param[1]}"]

    def leaseDuration(self, param: int) -> str | None:
        return None
    
    def leaseTerm(self, param: LeaseTerm) -> str | None:
        if param is LeaseTerm.ShortTerm or param is LeaseTerm.MonthToMonth:
            return 'short-term-available'
        return None

    def pets(self, param: bool) -> str | None:
        if param:
            return 'pet-friendly'
        return None

    def transit(self, param: bool) -> str | None:
        return None

    def composeUrl(self, query: Query) -> dict[UrlFieldType, Any]:
        queryDict = query.getQueryParamDict();
        locationArr = self.location(queryDict[QueryParam.Location])
        return {
            UrlFieldType.Prefix: None,
            UrlFieldType.PathPrefixes: [
                locationArr[0],
                f"{locationArr[1]}-{self.reType(queryDict[QueryParam.REType])}"
            ],
            UrlFieldType.Params: [
                self.bedrooms(queryDict[QueryParam.Bedrooms]),
                *self.priceRange(queryDict[QueryParam.PriceRange]),
                self.leaseDuration(queryDict[QueryParam.LeaseDuration]),
                self.leaseTerm(queryDict[QueryParam.LeaseTerm]),
                self.pets(queryDict[QueryParam.Pets])
            ]
        }