from abc import ABC, abstractmethod
from typing import Any
from Listing import Listing, ListingField, ListingMap

class ListingService(ABC):
    @abstractmethod
    def parseLocation(str) -> dict[str, Any]:
        ...

    @abstractmethod
    def parseBedroomRange(str) -> list[int]:
        ...
    
    @abstractmethod
    def parsePrice(str) -> int:
        ...
    
    @abstractmethod
    def parseShortestLease(str) -> int:
        ...

    @abstractmethod
    def getSpecialFieldName(self, field: ListingField) -> str:
        ...

    def getFieldValue(self, listing: Listing, field: ListingField) -> Any:
        return listing.dict()[ListingMap[field]]
    