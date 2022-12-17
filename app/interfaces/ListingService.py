from abc import ABC, abstractmethod
from typing import Any
from ..models.Listing import Listing
from ..enums import ListingField
from ..constants import listingMap
from ..models.TagModel import TagModel
from geopy.location import Location

class ListingService(ABC):
    @abstractmethod
    def getProviderName(self) -> str:
        ...

    @abstractmethod
    def getOnSuccessTag(self) -> TagModel:
        ...

    @abstractmethod
    def parseName(self, nameStr: str) -> str:
        ...

    @abstractmethod
    def parseLocation(self, locStr: str, queryVal: Any | None = None) -> Location:
        ...

    @abstractmethod
    def parseBedroomOptions(self, opts: str, queryVal: Any | None = None) -> list[int]:
        ...
    
    @abstractmethod
    def parsePrice(self, price: str, queryVal: Any | None = None) -> int:
        ...
    
    @abstractmethod
    def parseShortestLease(self, lease: str, queryVal: Any | None = None) -> int:
        ...

    @abstractmethod
    def getFieldMaps(self) -> dict[ListingField, list[TagModel] | None]:
        ...

    @abstractmethod
    def getSpecialFieldName(self, field: ListingField) -> str | None:
        ...

    def getFieldValue(self, listing: Listing, field: ListingField) -> Any:
        return listing.dict()[listingMap[field]]

    def parse(self, field: ListingField, val: str, queryVal: Any | None = None) -> Any:
        match(field):
            case ListingField.Name:
                return self.parseName(val)
            case ListingField.Location:
                return self.parseLocation(val, queryVal)
            case ListingField.Bedrooms:
                return self.parseBedroomOptions(val, queryVal)
            case ListingField.Price:
                return self.parsePrice(val, queryVal)
            case ListingField.ShortestLease:
                return self.parseShortestLease(val, queryVal)
            case _:
                return None
    