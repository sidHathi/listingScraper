from enum import Enum

class ListingField(Enum):
    Url = 1
    ProviderName = 2
    Name = 3
    Location = 4
    REType = 5
    Bedrooms = 6
    Price = 7
    ShortestLease = 8
    Pets = 9
    Transit = 10

class QueryParam(Enum):
    Location = 1
    REType = 2
    Bedrooms = 3
    PriceRange = 4
    LeaseTerm = 5
    LeaseDuration = 6
    Pets = 7
    Transit = 8
    
class REType(Enum):
    House = 1
    Apartment = 2
    Condo = 3
    SharedSpace = 4

class LeaseTerm(Enum):
    MonthToMonth = 1
    ShortTerm = 2
    DateRange = 3
    LongTerm = 4
    Specific = 5

class UrlFieldType(Enum):
    Prefix = 1
    PathPrefixes = 2
    Params = 3