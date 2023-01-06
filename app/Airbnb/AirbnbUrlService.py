import re
from geopy.location import Location
from typing import Any
from datetime import datetime, timedelta

from ..interfaces.UrlService import UrlService
from ..enums import REType, LeaseTerm, UrlFieldType
from ..models.Query import Query
from ..utils.scrapingUtils import parseGMV3Location, parseNominatimLocation
from ..constants import termToMonthMap

class AirbnbUrlService(UrlService):
    def baseUrl(self) -> str:
        return 'https://airbnb.com/'
    
    def paramSeparator(self) -> str:
        return '&'
    
    def usesQueryParams(self) -> bool:
        return True
    
    def location(self, queryLocation: Location) -> list[str]:
        city, state = parseNominatimLocation(queryLocation) or parseGMV3Location(location=queryLocation, shortened=True) or [None, None]
        if city is None or state is None:
            return []
        cityStr, stateStr = (re.sub(' ', '-', city.capitalize()), re.sub(' ', '-', state.capitalize()))
        return [f'{cityStr}-{stateStr}']
    
    def reType(self, param: REType) -> str | None:
        return None
    
    def bedrooms(self, param: int) -> str | None:
        return 'adults=' + '{' + f'{param}' + '}'
    
    def priceRange(self, param: list[int]) -> list[str]:
        if len(param) < 2:
            return []
        return [f'price_min={param[0]}&price_max={param[1]}']
    
    def leaseTerm(self, param: LeaseTerm) -> str | None:
            numDays: int | None = 30*((termToMonthMap[param] or 12) + 1)
            return f'price_filter_num_nights={numDays}'
            
    def leaseDuration(self, param: int) -> str | None:
        return None
    
    def pets(self, param: bool) -> str | None:
        return None
    
    def transit(self, param: bool) -> str | None:
        return None
    
    def getQueryLocationString(self, location: Location) -> str:
        city, state = parseNominatimLocation(location) or parseGMV3Location(location, shortened=True) or [None, None]
        if city is None or state is None:
            return ''
        
        return f'query={city}%2C%20{state}'
    
    def getRefinementPaths(self, leaseTerm: LeaseTerm) -> str:
        '''
        TODO: Implement such that this returns the string refinement_paths%5B%5D=%2fhomes&checkin={YEAR_MONTH_DAY}&checkout={YEAR_MONTH_DAY} where dates are formatted, start date is tomorrow, and end date is based on lease term
        '''

        numDays: int = 30*((termToMonthMap[leaseTerm] or 12) + 1)
        startDate: str = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        endDate: str = (datetime.now() + timedelta(days=numDays)).strftime("%Y-%m-%d")

        return f'refinement_paths%5B%5D=%2fhomes&checkin={startDate}&checkout={endDate}'

    def composeUrl(self, query: Query) -> dict[UrlFieldType, Any]:
        queryDict = query.getQueryParamDict
        refinementPaths: str = self.getRefinementPaths(query.leaseTerm)
        filterString: str = 'search_type=filter_change&tab_id=home_tab&flexible_trip_lengths%5B%5D=one_month&price_filter_input_type=1'
        return {
            UrlFieldType.Prefix : None,
            UrlFieldType.PathPrefixes: [
                '/s',
                *self.location(query.location),
                'homes'
            ],
            UrlFieldType.Params: [
                self.bedrooms(query.bedrooms),
                refinementPaths,
                filterString,
                self.leaseTerm(query.leaseTerm),
                *self.priceRange(query.priceRange),
            ],
        }