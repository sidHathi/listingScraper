from pydantic import BaseModel, ValidationError, validator
from geopy.geocoders import Nominatim
from geopy.location import Location
from QueryParams import QueryParam
from QueryParams import REType
from QueryParams import LeaseTerm

class Query(BaseModel):
    location: Location
    reType: REType
    bedrooms: int # 0 for studio
    priceRange: list[int] #[min, max]
    leaseDuration: int # in months or days TBD
    leaseTerm: LeaseTerm

    @validator('bedrooms')
    def validate_bedrooms(cls, v):
        if v < 0 or v > 10:
            raise ValueError('must be within range [0, 10]')
        return v.title()

    @validator('priceRange')
    def validate_price_range(cls, v):
        if (len(v) < 2 or (v[0] >= v[1])):
            raise ValueError('must be of form [min, max]')
        return v.title()

    def getQueryParamDict(self) -> dict:
        return {
            QueryParam.Location: self.location,
            QueryParam.REType: self.reType,
            QueryParam.Bedrooms: self.bedrooms,
            QueryParam.PriceRange: self.priceRange,
            QueryParam.LeaseTerm: self.leaseTerm,
            QueryParam.LeaseDuration: self.leaseDuration
        }