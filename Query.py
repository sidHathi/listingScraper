from pydantic import BaseModel, validator
from geopy.location import Location
from QueryParams import QueryParam
from QueryParams import REType
from QueryParams import LeaseTerm
from Listing import ListingField
from typing import Any
from constants import termToMonthMap

class Query(BaseModel):
    location: Location
    reType: REType
    bedrooms: int # 0 for studio
    priceRange: list[int] #[min, max]
    leaseTerm: LeaseTerm
    leaseDuration: int | None # in months or days TBD

    @validator('leaseDuration')
    def validate_leaseDuration(cls, v, values):
        if v is None:
            print(values)
            return termToMonthMap[values['leaseTerm']]
        return v

    @validator('bedrooms')
    def validate_bedrooms(cls, v):
        if v < 0 or v > 10:
            raise ValueError('must be within range [0, 10]')
        return v

    @validator('priceRange')
    def validate_price_range(cls, v):
        if (len(v) < 2 or (v[0] >= v[1])):
            raise ValueError('must be of form [min, max]')
        return v

    def getQueryParamDict(self) -> dict[QueryParam, Any]:
        return {
            QueryParam.Location: self.location,
            QueryParam.REType: self.reType,
            QueryParam.Bedrooms: self.bedrooms,
            QueryParam.PriceRange: self.priceRange,
            QueryParam.LeaseTerm: self.leaseTerm,
            QueryParam.LeaseDuration: self.leaseDuration
        }
    
    def getCorrespondingField(self, param: QueryParam) -> ListingField | None:
        match param:
            case QueryParam.Location:
                return ListingField.Location
            case QueryParam.REType:
                return ListingField.REType
            case QueryParam.Bedrooms:
                return ListingField.Bedrooms
            case QueryParam.LeaseDuration:
                return ListingField.ShortestLease
        return None

    def getCorrespondingParam(self, field: ListingField) -> QueryParam | None:
        match field:
            case ListingField.Location:
                return QueryParam.Location
            case ListingField.REType:
                return QueryParam.REType
            case ListingField.Bedrooms:
                return QueryParam.Bedrooms
            case ListingField.ShortestLease:
                return QueryParam.LeaseDuration
        return None
    
    class Config:
        arbitrary_types_allowed = True