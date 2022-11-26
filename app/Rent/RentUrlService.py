from ..interfaces.UrlService import UrlService
from geopy.location import Location
from ..enums import QueryParam, REType, LeaseTerm
from ..models.Query import Query
from typing import Any
from ..interfaces.UrlService import UrlFieldType
import re

class RentUrlService(UrlService):
    def baseUrl(self) -> str:
        return 'https://www.rent.com/'

    def paramSeparator(self) -> str:
        return '_'

    def location(self, queryLocation: Location) -> list[str]:
        addr = queryLocation.raw['address']
        if 'city' not in addr or 'state' not in addr:
            return []
        return [re.sub(' ', '-', addr['state'].lower()), re.sub(' ', '-', addr['city'].lower())]
    
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

    def priceRange(self, param: list[int]) -> str | None:
        if (len(param) < 2):
            return None
        return f"max-price-{param[1]}"

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
                self.priceRange(queryDict[QueryParam.PriceRange]),
                self.leaseDuration(queryDict[QueryParam.LeaseDuration]),
                self.leaseTerm(queryDict[QueryParam.LeaseTerm]),
                self.pets(queryDict[QueryParam.Pets])
            ]
        }