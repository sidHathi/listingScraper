from pydantic import BaseModel, validator
from enum import Enum
from typing import Any
from QueryParams import REType, LeaseTerm

class ListingField(Enum):
    Location = 1
    REType = 2
    Bedrooms = 3
    Price = 4
    ShortestLease = 5
    # TO-DO: Add additional fields

ListingMap: dict[ListingField, str] = {
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
    location: dict[str, Any]
    reType: REType
    bedrooms: list[int] # is often a range
    price: int
    shortestLease: int # in months

    @validator('bedrooms')
    def validate_bedrooms(cls, v):
        if (len(v) < 2 or (v[0] >= v[1])):
            raise ValueError('must be of form [min, max]')
        return v

    def setAttr(self, field: ListingField, newVal: Any) -> None:
        key = ListingMap[field]
        obj = self.dict()
        obj[key] = newVal
        self.parse_obj(obj)

    def getAttr(self, field: ListingField) -> Any:
        return self.dict()[ListingMap[field]]
        


    
