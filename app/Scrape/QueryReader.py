from typing import Any, cast
from geopy.location import Location
from geopy.geocoders import Nominatim, GoogleV3
from geopy.extra.rate_limiter import RateLimiter
from dotenv import dotenv_values

from ..DBInterface import DBInterface
from ..models.Query import Query
from ..enums import REType, LeaseTerm
from ..constants import reversedEnumMaps

config = dotenv_values('.env')

class QueryReader:
    def __init__(self, dbInterface):
        self.dbInterface = dbInterface
        self.results: list[dict[str, Any]] = []

    def getQueryData(self):
        self.results = self.dbInterface.getQueries()

    def parseLocation(self, locStr: str) -> Location:
        geocoder = GoogleV3(api_key=config['GOOGLE_MAPS_API_KEY'])
        geocode = RateLimiter(geocoder.geocode, min_delay_seconds=1, return_value_on_exception=None)
        loc = geocode(locStr)
        if loc is None:
            return Location(locStr, (0.0, 0.0, 0.0), {})
        cast(Location, loc)
        assert type(loc) is Location
        print(loc)
        return loc

    def getQueryList(self) -> list[Query]:
        self.getQueryData()
        if len(self.results) < 1:
            return []
        
        return list(map(
            lambda res: 
            Query(
                name=res['name'],
                location=cast(Location, self.parseLocation(res['location'])),
                reType=cast(REType, reversedEnumMaps['REType'][res['reType']]),
                bedrooms=res['bedrooms'],
                priceRange=res['priceRange'],
                leaseTerm=cast(LeaseTerm, reversedEnumMaps['LeaseTerm'][res['leaseTerm']]),
                leaseDuration=res['leaseDuration'],
                pets=res['pets'],
                transit=res['transit'],
                hasProxyPermission=res['hasProxyPermission']
            ), 
            self.results
        ))