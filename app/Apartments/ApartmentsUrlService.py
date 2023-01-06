from typing import Any
from geopy.location import Location
import re

from ..interfaces.UrlService import UrlService
from ..enums import LeaseTerm, REType, UrlFieldType, QueryParam
from ..models.Query import Query
from ..utils.scrapingUtils import parseGMV3Location, parseNominatimLocation

class ApartmentsUrlService(UrlService):
    def baseUrl(self) -> str:
        return 'https://www.apartments.com'
    
    def paramSeparator(self) -> str:
        return '/'
    
    def usesQueryParams(self) -> bool:
        return False
    
    def location(self, queryLocation: Location) -> list[str]:
        city, state = parseNominatimLocation(queryLocation) or parseGMV3Location(location=queryLocation, shortened=True) or [None, None]
        if city is None or state is None:
            return []
        cityStr, stateStr = (re.sub(' ', '-', city.lower()), re.sub(' ', '-', state.lower()))
        return [f'{cityStr}-{stateStr}']
    
    def reType(self, param: REType) -> str | None:
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
        normalizedParam: int = min(param, 4)
        return f'min-{normalizedParam}-bedrooms'
    
    def priceRange(self, param: list[int]) -> list[str]:
        if len(param) < 2:
            return []
        normalizedMin = max(param[0], 200)
        normalizedMax = max(param[1], 200)
        return [f'{normalizedMin}-to-{normalizedMax}']
    
    def leaseTerm(self, param: LeaseTerm) -> str | None:
        if param is LeaseTerm.ShortTerm or param is LeaseTerm.MonthToMonth:
            return 'short-term'
        return None

    def leaseDuration(self, param: int) -> str | None:
        return None
    
    def pets(self, param: bool) -> str | None:
        if param: 
            return 'pet-friendly'
        return None
    
    def transit(self, param: bool) -> str | None:
        return None
    
    def composeUrl(self, query: Query) -> dict[UrlFieldType, Any]:
        queryDict = query.getQueryParamDict()
        compositeParamStr: str = self.priceRange(queryDict[QueryParam.PriceRange])[0]
        if queryDict[QueryParam.Bedrooms] is not None:
            compositeParamStr = f'{self.bedrooms(queryDict[QueryParam.Bedrooms])}-{compositeParamStr}'
        if queryDict[QueryParam.Pets]:
            compositeParamStr += f'-{self.pets(queryDict[QueryParam.Pets])}'

        return {
            UrlFieldType.Prefix: None,
            UrlFieldType.PathPrefixes: None,
            UrlFieldType.Params: [
                self.reType(queryDict[QueryParam.REType]),
                *self.location(queryDict[QueryParam.Location]),
                compositeParamStr,
                self.leaseTerm(queryDict[QueryParam.LeaseTerm])
            ]
        }
    
    def construct(self, query: Query):
        return super().construct(query)
