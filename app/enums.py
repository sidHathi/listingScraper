from enum import Enum

class ListingField(Enum):
    Url = 1
    Name = 2
    Location = 3
    REType = 4
    Bedrooms = 5
    Price = 6
    ShortestLease = 7
    Pets = 8
    Transit = 9

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