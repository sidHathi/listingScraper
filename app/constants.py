from typing import Any
from enum import Enum

from .enums import LeaseTerm, REType
from .enums import ListingField
from .models.TagModel import TagModel
from .utils.genUtils import reverseDict

keywordMap: dict[str, LeaseTerm] = {
    "short-term": LeaseTerm.ShortTerm,
    "short term": LeaseTerm.ShortTerm,
    "shortTerm": LeaseTerm.ShortTerm,
    "variable": LeaseTerm.ShortTerm,
    "month-to-month": LeaseTerm.MonthToMonth,
    "month to month": LeaseTerm.MonthToMonth,
    "long term": LeaseTerm.LongTerm,
    "long-term": LeaseTerm.LongTerm,
}

termToMonthMap: dict[LeaseTerm, int | None] = {
    LeaseTerm.MonthToMonth: 1,
    LeaseTerm.ShortTerm: 4,
    LeaseTerm.DateRange: None,
    LeaseTerm.LongTerm: 12,
    LeaseTerm.Specific: None
}

listingMap: dict[ListingField, str] = {
    ListingField.Url: 'url',
    ListingField.ProviderName: 'providerName',
    ListingField.Name: 'name',
    ListingField.Location: 'location',
    ListingField.REType: 'reType',
    ListingField.Bedrooms: 'bedrooms',
    ListingField.Price: 'price',
    ListingField.ShortestLease: 'shortestLease',
    ListingField.Pets: 'pets',
    ListingField.Transit: 'transit'
}

enumMaps: dict[str, dict[Enum, str]] = {
    'REType': {
        REType.House: 'house',
        REType.Apartment: 'apartment',
        REType.Condo: 'condo',
        REType.SharedSpace: 'shared-space'
    },
    'LeaseTerm': {
        LeaseTerm.ShortTerm: 'shortTerm',
        LeaseTerm.MonthToMonth: 'monthToMonth',
        LeaseTerm.DateRange: 'dateRange',
        LeaseTerm.LongTerm: 'longTerm',
        LeaseTerm.Specific: "specific"
    }
}

reversedEnumMaps: dict[str, dict[str, Enum]] = dict(zip(
    list(enumMaps.keys()), 
    list(map(
        lambda preRev: reverseDict(preRev),
        list(enumMaps.values())
    ))
))

rentSearchingTag: TagModel = TagModel(identifiers={
    'data-tid': 'pdp-link', 
    'data-tag_item': 'property_title'
})

fbmSearchingTag: TagModel = TagModel(identifiers={
    'role': 'link',
    'class': 'x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g x1lku1pv'
})

fieldDefaults: dict[ListingField, Any] = {
    ListingField.Url: 'unavailable',
    ListingField.Name: 'unavailable',
    ListingField.Location: None,
    ListingField.REType: REType.Apartment,
    ListingField.Bedrooms: 0,
    ListingField.Price: -1,
    ListingField.ShortestLease: 12,
    ListingField.Pets: False,
    ListingField.Transit: False,
}

providerNames: list[str] = [
    'facebook',
    'rent.com'
]
