from .enums import LeaseTerm, REType
from .enums import ListingField
from enum import Enum
from .models.TagModel import TagModel
from typing import Any

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
    }
}

rentSearchingTag: TagModel = TagModel(identifiers={
    'data-tid': 'pdp-link', 
    'data-tag_item': 'property_title'
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
