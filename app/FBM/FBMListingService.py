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

        return super().parseLocation(locStr=addr, queryVal=queryVal)

    def parseBedroomOptions(self, opts: str, queryVal: Any | None = None) -> list[int]:
        return super().parseBedroomOptions(opts, queryVal)

    def parsePrice(self, price: str, queryVal: Any | None = None) -> int:
        return super().parsePrice(price, queryVal)

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
                    'class': 'xb57i2i x1q594ok x5lxg6s x78zum5 xdt5ytf x6ikm8r x1ja2u2z x1pq812k x1rohswg xfk6m8 x1yqm8si xjx87ck x1l7klhg xs83m0k x2lwn1j xx8ngbg xwo3gff x1oyok0e x1odjw0f x1e4zzel x1n2onr6 xq1qtft x1iyjqo2 xqtp20y xx6bls6 xh8yej3 xiylbte'
                }),
            ],
            ListingField.ShortestLease: [
                TagModel(tagType='div', identifiers={
                    'class': 'xb57i2i x1q594ok x5lxg6s x78zum5 xdt5ytf x6ikm8r x1ja2u2z x1pq812k x1rohswg xfk6m8 x1yqm8si xjx87ck x1l7klhg xs83m0k x2lwn1j xx8ngbg xwo3gff x1oyok0e x1odjw0f x1e4zzel x1n2onr6 xq1qtft x1iyjqo2 xqtp20y xx6bls6 xh8yej3 xiylbte'
                }),
            ],
            ListingField.Pets: None, # use query val
            ListingField.Transit: None # use query val
        }

    def getSpecialFieldName(self, field: ListingField) -> str | None:
        return None