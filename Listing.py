from pydantic import BaseModel, validator
from enum import Enum
from typing import Any
from QueryParams import REType, LeaseTerm
from geopy.location import Location

class ListingField(Enum):
    Name = 1
    Location = 2
    REType = 3
    Bedrooms = 4
    Price = 5
    ShortestLease = 6
    # TO-DO: Add additional fields

ListingMap: dict[ListingField, str] = {
    ListingField.Name: 'name',
    ListingField.Location: 'location',
    ListingField.REType: 'reType',
    ListingField.Bedrooms: 'bedrooms',
    ListingField.Price: 'price',
    ListingField.ShortestLease: 'shortestLease',
}

class Listing(BaseModel):
    '''
    TO-DO: Implementing listing object model
    '''
    name: str
    location: Location
    reType: REType
    bedrooms: list[int] # is often a range
    price: int
    shortestLease: int # in months

    @validator('bedrooms')
    def validate_bedrooms(cls, v):
        if (len(v) < 2 or (v[0] > v[1])):
            raise ValueError('must be of form [min, max]')
        return v

    def setAttr(self, field: ListingField, newVal: Any) -> None:
        key = ListingMap[field]
        obj = self.dict()
        obj[key] = newVal
        self.parse_obj(obj)

    def getAttr(self, field: ListingField) -> Any:
        return self.dict()[ListingMap[field]]

    class Config:
        arbitrary_types_allowed = True
        


    
