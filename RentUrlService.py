from UrlService import UrlService
from geopy.location import Location
from QueryParams import QueryParam, REType, LeaseTerm
from Query import Query

class RentUrlService(UrlService):
    def url(self) -> str:
        return 'https://www.rent.com/'

    def paramSeparator(self) -> str:
        return '_'

    def location(self, queryLocation: Location) -> list[str]:
        addr = queryLocation.raw['address']
        return [addr.get('state'), addr.get('city', '')]
    
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

    def composeUrl(self, query: Query):
        queryDict = query.getQueryParamDict();
        locationArr = queryDict[QueryParam.Location]
        return {
            'prefix': None,
            'pathPrefixes': [
                locationArr[0],
                f"{locationArr[1]}-{self.reType(queryDict[QueryParam.REType])}"
            ],
            'params': [
                self.bedrooms(queryDict[QueryParam.Bedrooms]),
                self.priceRange(queryDict[QueryParam.PriceRange]),
                self.leaseDuration(queryDict[QueryParam.LeaseDuration]),
                self.leaseTerm(queryDict[QueryParam.LeaseTerm])
            ]
        }