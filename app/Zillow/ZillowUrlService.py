from typing import Any
from geopy.location import Location
import re

from ..enums import QueryParam, REType, LeaseTerm, UrlFieldType
from ..models.Query import Query
from ..interfaces.UrlService import UrlService
from ..constants import usStateToAbbrev
from ..utils.scrapingUtils import parseGMV3Location, parseNominatimLocation

class ZillowUrlService(UrlService):
    def baseUrl(self) -> str:
        return 'https://www.zillow.com/'
    
    def paramSeparator(self) -> str:
        return '%7D%2C%22'

    def usesQueryParams(self) -> bool:
        return True

    def location(self, queryLocation: Location) -> list[str]:
        city, state = parseNominatimLocation(queryLocation) or parseGMV3Location(location=queryLocation, shortened=True) or [None, None]
        if city is None or state is None:
            return []
        cityStr, stateStr = (re.sub(' ', '-', city.lower()), re.sub(' ', '-', state.lower()))
        return [f'{cityStr}-{stateStr}']

    def reType(self, param: REType) -> str:
        return 'rentals'
        # match(param):
        #     case REType.Apartment:
        #         return 'apartments'
        #     case REType.House:
        #         return 'rent-houses'
        #     case REType.Condo:
        #         return 'apartments'
        #     case _:
        #         return 'invalid param'

    def bedrooms(self, param: int) -> str | None:
        baseStr: str = 'beds%22%3A%7B%22min%22%3A'
        normalizedParam: int = max(param , 1)
        # normalizedParam: int = 1
        return f'{baseStr}{normalizedParam}'

    def priceRange(self, param: list[int]) -> list[str]:
        if len(param) < 2:
            return []
        baseStr: str = 'mp%22%3A%7B%22'
        minStr: str = f'min%22%3A{max(100, param[0])}'
        maxStr: str = f'max%22%3A{max(100, param[1])}'
        return [f'{baseStr}{minStr}%2C%22{maxStr}']

    def leaseTerm(self, param: LeaseTerm) -> str | None:
        if param is LeaseTerm.ShortTerm or param is LeaseTerm.MonthToMonth:
            return 'short%20term'
        return None

    def leaseDuration(self, param: int) -> str | None:
        return None

    def pets(self, param: bool) -> str | None:
        if param:
            return 'sdog%22%3A%7B%22value%22%3Atrue%7D%'
        return None

    def transit(self, param: bool) -> str | None:
        if param:
            return 'transit'
        return None

    def composeUrl(self, query: Query) -> dict[UrlFieldType, Any]:
        queryDict = query.getQueryParamDict();
        baseStr: str = 'searchQueryState=%7B%22filterState%22%3A%7B%22price%22%3A%7B%22min%22%3A81035%2C%22max%22%3A445692%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22mf%22%3A%7B%22value%22%3Afalse'
        str2: str = 'auc%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse'
        str3: str = 'sf%22%3A%7B%22value%22%3Afalse%7D%2C%22tow%22%3A%7B%22value%22%3Afalse%7D%2C%22sdog%22%3A%7B%22value%22%3Atrue'
        keyWordStr: str = ''
        if queryDict[QueryParam.Transit] and queryDict[QueryParam.LeaseTerm]:
            keyWordStr = f'att%22%3A%7B%22value%22%3A%22{self.leaseTerm(queryDict[QueryParam.LeaseTerm])}%2C%20{self.transit(queryDict[QueryParam.Transit])}%22%7D'
        elif queryDict[QueryParam.LeaseTerm]:
            keyWordStr = f'att%22%3A%7B%22value%22%3A%22{self.leaseTerm(queryDict[QueryParam.LeaseTerm])}%22%7D'
        elif queryDict[QueryParam.Transit]:
            keyWordStr = f'att%22%3A%7B%22value%22%3A%22{self.leaseTerm(queryDict[QueryParam.Transit])}%22%7D'
        listStr: str = 'isListVisible%22%3Atrue%7D'
        return {
            UrlFieldType.Prefix: None,
            UrlFieldType.PathPrefixes: [
                *self.location(queryDict[QueryParam.Location]),
                self.reType(queryDict[QueryParam.REType]),
            ],
            UrlFieldType.Params: [
                baseStr,
                *self.priceRange(queryDict[QueryParam.PriceRange]),
                str2,
                self.bedrooms(queryDict[QueryParam.Bedrooms]),
                str3,
                keyWordStr,
                listStr
            ]
        }


