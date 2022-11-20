from geopy.location import Location
from QueryParams import REType
from QueryParams import LeaseTerm
from abc import ABC, abstractmethod

class UrlService(ABC):
    @abstractmethod
    def location(self, queryLocation: Location) -> str:
        """Get the location string for the url"""
        ...

    @abstractmethod
    def reType(self, param: REType) -> str:
        """Get the real estate type string for the url"""
        ...

    @abstractmethod
    def bedrooms(self, param: int) -> str:
        """Get the bedrooms string for the url"""
        ...

    @abstractmethod
    def priceRange(self, param: list[int]) -> str:
        """Get the price range string for the url"""
        ...

    @abstractmethod
    def leaseDuration(self, param: int) -> str:
        """Get the lease duration string for the url"""
        ...

    @abstractmethod
    def leaseTerm(self, param: LeaseTerm) -> str:
        """Get the lease term sting for the url"""
        ...
