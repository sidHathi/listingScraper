from typing import Any, Coroutine, cast
from geopy.geocoders import Nominatim
from geopy.location import Location
from geopy.exc import GeocoderTimedOut, GeocoderParseError, GeocoderServiceError, GeocoderUnavailable
import re

from ..interfaces.ListingService import ListingService
from ..utils.scrapingUtils import findIntegerListMonths, matchLeaseTermByKeyword, findCityStatePair, findCompleteAddress, findPrice, encodeLocation
from ..constants import keywordMap, termToMonthMap
from ..enums import ListingField, LeaseTerm
from ..models.TagModel import TagModel

class FBMListingService(ListingService):
    def getProviderName(self) -> str:
        return "facebook"

    def getOnSuccessTag(self) -> TagModel:
        return TagModel(tagType='h1', identifiers={'class':'x1heor9g x1qlqyl8 x1pd3egz x1a2a7pz x193iq5w xeuugli'})

    def parseName(self, nameStr: str) -> str:
        return nameStr

    def parseLocation(self, locStr: str, queryVal: Any | None = None) -> Location:
        addr = findCompleteAddress(locStr)
        if addr is None:
            addr = findCityStatePair(locStr)
        if addr is None:
            assert queryVal is not None
            return queryVal

        location: Location | None = encodeLocation(addr)
        if location is None:
            assert queryVal is not None
            return queryVal
        return location

    def parseBedroomOptions(self, opts: str, queryVal: Any | None = None) -> list[int]:
        '''
        format {range Bed/Beds OR Studio}
        '''
        print(opts)
        studioMatches: list[str] = re.findall(r'(studio)', opts, re.IGNORECASE)
        if len(studioMatches) > 0:
            return [0, 0] # must be 'Studio'
        
        bedsRegexMatch = re.search(r'([\d\s]+(beds|bed))', opts, re.I)
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

    def parsePrice(self, price: str, queryVal: Any | None = None) -> int:
        print("[PRICE]: " +price);
        numeric = findPrice(price)
        print(numeric)
        if numeric is None or numeric == '':
            return -1

        return int(numeric)

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

    def getFieldMaps(self) -> dict[ListingField, list[TagModel] | None]:
         return {
            ListingField.Url: None,
            ListingField.Name: [
                TagModel(tagType='div', identifiers={
                    'class': 'x78zum5 x1iyjqo2 x1n2onr6 xdt5ytf'
                }),
                TagModel(tagType='div', identifiers={
                    'class': 'xyamay9 x1pi30zi x18d9i69 x1swvt13'
                }),
                TagModel(tagType='h1', identifiers={
                    'class': 'x1heor9g x1qlqyl8 x1pd3egz x1a2a7pz x193iq5w xeuugli'
                })
            ],
            ListingField.Location: [
                TagModel(tagType='div', identifiers={
                    'class': 'x1xmf6yo'
                }),
                TagModel(tagType='div', identifiers={
                    'class': 'xwib8y2'
                }),
                TagModel(tagType='div', identifiers={
                    'class': 'xjyslct xjbqb8w x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1rg5ohu xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1n2onr6 x16tdsg8 xh8yej3'
                })
            ],
            ListingField.REType: None, # use query val
            ListingField.Bedrooms: [
                TagModel(tagType='div', identifiers={
                    'class': 'xb57i2i x1q594ok x5lxg6s x78zum5 xdt5ytf x6ikm8r x1ja2u2z x1pq812k x1rohswg xfk6m8 x1yqm8si xjx87ck x1l7klhg xs83m0k x2lwn1j xx8ngbg xwo3gff x1oyok0e x1odjw0f x1e4zzel x1n2onr6 xq1qtft x1iyjqo2 xqtp20y xx6bls6 xh8yej3 xiylbte'
                }),
            ],
            ListingField.Price: [
                TagModel(tagType='div', identifiers={
                    'class': 'xyamay9 x1pi30zi x18d9i69 x1swvt13'
                }),
                TagModel(tagType='div', identifiers={
                    'class': 'x78zum5 x1xmf6yo'
                }),
                TagModel(tagType='div', identifiers={
                    'class': 'x1anpbxc'
                }),
                TagModel(tagType='span', identifiers={
                    'class': 'x193iq5w xeuugli x13faqbe x1vvkbs xlh3980 xvmahel x1n0sxbx x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x3x7a5m x1lkfr7t x1lbecb7 x1s688f xzsf02u'
                })
            ],
            ListingField.ShortestLease: [
                TagModel(tagType='div', identifiers={
                    'class': 'xod5an3'
                }),
                TagModel(tagType='div', identifiers={
                    'class': 'xexx8yu x1pi30zi x18d9i69 x1swvt13'
                }),
                TagModel(tagType='div', identifiers={
                    'class': 'xz9dl7a x4uap5 xsag5q8 xkhd6sd x126k92a'
                }),
                TagModel(tagType='span', identifiers={
                    'class': 'x193iq5w xeuugli x13faqbe x1vvkbs xlh3980 xvmahel x1n0sxbx x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x3x7a5m x6prxxf xvq8zen xo1l8bm xzsf02u'
                })
            ],
            ListingField.Pets: None, # use query val
            ListingField.Transit: None # use query val
        }

    def getSpecialFieldName(self, field: ListingField) -> str | None:
        return None