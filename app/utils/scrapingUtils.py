from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
from typing import Any, cast
import re
from geopy import Location
from geopy.geocoders import GoogleV3
from geopy.exc import GeocoderAuthenticationFailure, GeocoderInsufficientPrivileges, GeocoderNotFound, GeocoderParseError, GeocoderQueryError, GeocoderQuotaExceeded, GeocoderRateLimited, GeocoderServiceError, GeocoderTimedOut, GeocoderUnavailable, GeopyError
from geopy.extra.rate_limiter import RateLimiter
from dotenv import dotenv_values

from ..models.TagModel import TagModel
from ..enums import LeaseTerm, ListingField
from ..constants import maxLocationRetires, termToMonthMap, keywordMap

config = dotenv_values('.env')

def encodeLocation(addressString: str) -> Location | None:
    if config['GOOGLE_MAPS_API_KEY'] is None:
        return None
    for _ in range(maxLocationRetires):
        try:
            geocoder = GoogleV3(api_key=config['GOOGLE_MAPS_API_KEY'])
            geocode = RateLimiter(geocoder.geocode, min_delay_seconds=1, return_value_on_exception=None)
            location = geocode(addressString)
            if location is None:
                continue
            cast(Location, location)
            return location
        except (GeocoderAuthenticationFailure, GeocoderInsufficientPrivileges, GeocoderNotFound, GeocoderParseError, GeocoderQueryError, GeocoderQuotaExceeded, GeocoderRateLimited, GeocoderServiceError, GeocoderTimedOut, GeocoderUnavailable, GeopyError) as e:
            print('location cast failed')
            print(e)
            continue
    return None

def parseGMV3Location(location: Location, shortened: bool = False) -> list[str] | None:
    locMap: dict[str, Any] = location.raw
    if 'address_components' not in locMap:
        return None
    
    city = ""
    state = ""
    addr_components: list[dict[str, Any]] = locMap['address_components']
    for comp in addr_components:
        if comp['types'][0] == 'locality' and 'long_name' in comp:
            city = comp['long_name']
        if comp['types'][0] == 'administrative_area_level_1':
            if shortened and 'short_name' in comp:
                state = comp['short_name']
            elif 'long_name' in comp:
                state = comp['long_name']
    return [city, state]

def parseNominatimLocation(location: Location) -> list[str] | None:
    if 'address' not in location.raw:
        return None
    addr: dict[str, Any] = location.raw['address']
    if 'city' not in addr or 'state' not in addr:
        return None
    return [addr['city'], addr['state']]
            
async def htmlPull(url: str, browser: webdriver.Chrome, timeout: int) -> str | None:
    try:
        browser.get(url)
        browser.implicitly_wait(timeout)
        return browser.page_source
    except WebDriverException:
        return None

def followTagMap(tagMap: list[TagModel], dom: BeautifulSoup) -> list[BeautifulSoup]:
    currentTagList = []
    for step in tagMap:
        if len(currentTagList) < 1:
            currentTagList = dom.find_all(step.tagType, step.identifiers)
            continue
        nextTagList = []
        for tag in currentTagList:
            nextTagList.extend(tag.find_all(step.tagType, step.identifiers))
        currentTagList = nextTagList
    return currentTagList

def queryToListingFieldConvert(field: Any, fieldType: ListingField):
    if fieldType is ListingField.Bedrooms:
        return [field, field]
    else:
        return field

def findIntegerMonths(domContent: str) -> list[int] | None:
    regex = re.compile(r'(\d+[-,\s]*(months|month))', re.IGNORECASE)
    matches = regex.findall(domContent)
    if matches is  None:
        return None
    def getMatchFromGroup(group):
        return group[0]
    matchingSubstrings: list[str] = list(map(getMatchFromGroup, matches))
    monthVals: list[int] = []
    added: set = set()
    if len(matchingSubstrings) < 1:
        return None
    for match in matchingSubstrings:
        split = re.split(r'[,\s]', match)
        assert(len(split) > 0)
        val = int(split[0])
        if val not in added:
            monthVals.append(val)
            added.add(val)
    return monthVals

def findIntegerListMonths(domContent: str) -> list[int] | None:
    regex = re.compile(r'([\d\s]+(,[\s\d]+)*\s*(or|and)*\s*\d*[-\s](months|month))', re.IGNORECASE)
    matches = regex.findall(domContent)
    if matches is  None:
        return None
    def getMatchFromGroup(group):
        return group[0]
    matchingSubstrings: list[str] = list(map(getMatchFromGroup, matches))
    monthVals: list[int] = []
    added: set = set()
    if len(matchingSubstrings) < 1:
        return None
    for match in matchingSubstrings:
        split = re.split(r'[,\s]', match)
        assert(len(split) > 0)
        for splitStr in split:
            valStr = re.sub(r'[^\d]', '', splitStr)
            if len(valStr) >= 1:
                val = int(valStr)
                if val not in added:
                    monthVals.append(val)
                    added.add(val)
    return monthVals

def matchRegex(matchString: str, searchString: str, flags: list[re.RegexFlag]) -> str | None:
    regex = re.compile(matchString, *flags)
    search = regex.search(searchString)
    if search is None:
        return None
    addr: str = search.group()
    return addr

def findCompleteAddress(domContent: str) -> str | None:
    return matchRegex(r'(\d+\s(\w+\s){1,4}(Ave|St|Rd|Dr|Cir|BLVD|CT|EXPY|FWY|LN|PKY|RD|SQ|TPKE)[\s,]{0,2}(NE|NW|SE|SW|E|W|N|S){0,1}[\s,]{0,2}([A-Za-z]+[\s,]{1,2}){0,3}[A-Z]{2,3}(\s\d+){0,1})', domContent, [re.IGNORECASE])

def findCityStatePair(domContent: str) -> str | None:
    return matchRegex(r'(([A-Z][a-z]+[\s,.]{0,2}){1,4}[A-Z]{2,3})', domContent, [])

def findPrice(domContent: str) -> str | None:
    priceStr = matchRegex(r'(\$[\d.,]+[\s\/]+)', domContent, [])
    if priceStr is None:
        return None
    
    numeric = re.sub(r'[^0-9]', '', priceStr)
    return numeric

def matchKeyword(domContent: str, keyword: str) -> bool:
    if keyword.upper() in map(str.upper, domContent):
        return True
    return False

def matchLeaseTermByKeyword(domContent: str, keyDict: dict[str, LeaseTerm]) -> list[LeaseTerm]:
    matches: list[LeaseTerm] = []
    for keyword in keyDict:
        if matchKeyword(domContent, keyword):
            matches.append(keyDict[keyword])
    return matches

def extractShortestLeaseFromDescription(description: str) -> int | None:
        listMatches = findIntegerListMonths(description)
        if listMatches is not None and len(listMatches) > 0:
            return min(listMatches)
        elif len(matchLeaseTermByKeyword(description, keywordMap)) > 0:
            val: int | None = termToMonthMap[matchLeaseTermByKeyword(description, keywordMap)[0]]
            if val is not None:
                return val
        return None