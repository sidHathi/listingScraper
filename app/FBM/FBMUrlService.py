from typing import Any
from geopy.location import Location
import re

from ..interfaces.UrlService import UrlService
from ..enums import REType, LeaseTerm, QueryParam, UrlFieldType
from .fbConstants import validLocations, shortenedLocations, quadTree, searchResultsMaxDist
from ..models.Query import Query

class FBMUrlService(UrlService):
    def baseUrl(self) -> str:
        return "https://facebook.com/marketplace/"

    def paramSeparator(self) -> str:
        return '&'

    def usesQueryParams(self) -> bool:
        return True

    def location(self, queryLocation: Location) -> list[str]:
        addr = queryLocation.raw['address']
        if 'city' not in addr:
            return []

        if addr['city'] in validLocations:
            cityStr = addr['city'].lower()
            if cityStr in shortenedLocations:
                cityStr = shortenedLocations[cityStr]
            return [cityStr]
        closestCityLoc = quadTree.getNearestLoc(queryLocation, searchResultsMaxDist)
        if closestCityLoc is None:
            return []
        cityStr = closestCityLoc.raw['address']['city'].lower()
        if cityStr in shortenedLocations:
            cityStr = shortenedLocations[cityStr]
        return [cityStr]

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
        return f"{param}-bedroom"
    
    def priceRange(self, param: list[int]) -> list[str]:
        if len(param) < 2:
            return []
        return [f"minPrice={param[0]}", f"maxPrice={param[1]}"]

    def leaseDuration(self, param: int) -> str | None:
        return None

    def leaseTerm(self, param: LeaseTerm) -> str | None:
        match param:
            case LeaseTerm.ShortTerm:
                return 'query=short%20term'
            case LeaseTerm.MonthToMonth:
                return 'query=month%20to%20month'
            case _:
                return None

    def pets(self, param: bool) -> str | None:
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
                f"{self.bedrooms(queryDict[QueryParam.Bedrooms])}-{self.reType(queryDict[QueryParam.REType])}"
            ],
            UrlFieldType.Params: [
                *self.priceRange(queryDict[QueryParam.PriceRange]),
                self.leaseTerm(queryDict[QueryParam.LeaseTerm]),
            ]
        }
    