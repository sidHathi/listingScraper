from pydantic import BaseModel, validator
from typing import Any
from ..enums import REType, ListingField
from geopy.location import Location
from ..constants import listingMap, enumMaps
from datetime import datetime

class Listing(BaseModel):
    # No optional fields for listings - 
    # default values should be set when unknown
    url: str
    providerName: str
    name: str
    location: Location
    reType: REType
    bedrooms: list[int] # is often a range
    price: int
    shortestLease: int # in months
    pets: bool
    transit: bool
    # TO-DO: Add furnished field

    @validator('bedrooms')
    def validate_bedrooms(cls, v):
        if (len(v) < 2 or (v[0] > v[1])):
            raise ValueError('must be of form [min, max]')
        return v

    def setAttr(self, field: ListingField, newVal: Any) -> None:
        key = listingMap[field]
        obj = self.dict()
        obj[key] = newVal
        self.parse_obj(obj)

    def getAttr(self, field: ListingField) -> Any:
        return self.dict()[listingMap[field]]

    def toJson(self) -> dict[str, Any]:
        json = self.dict()
        json['location'] = {
            'long' : self.location.longitude,
            'lat' : self.location.latitude,
            'address': self.location.address
        }
        json['reType'] = enumMaps['REType'][self.reType]
        json['scrapeTime'] = datetime.today().replace(microsecond=0)
        return json

    class Config:
        arbitrary_types_allowed = True
        


    
