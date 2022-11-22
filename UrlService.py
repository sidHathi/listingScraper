from geopy.location import Location
from QueryParams import QueryParam
from QueryParams import REType
from QueryParams import LeaseTerm
from abc import ABC, abstractmethod
from Query import Query
from enum import Enum
from typing import Any

class UrlFieldType(Enum):
    Prefix = 1
    PathPrefixes = 2
    Params = 3

class UrlService(ABC):
    @abstractmethod
    def baseUrl(self) -> str:
        '''return the url'''
        ...
    
    @abstractmethod
    def paramSeparator(self) -> str:
        '''return the url param separator char'''
        ...

    @abstractmethod
    def location(self, queryLocation: Location) -> list[str]:
        """Get the location string for the url"""
        ...

    @abstractmethod
    def reType(self, param: REType) -> str:
        """Get the real estate type string for the url"""
        ...

    @abstractmethod
    def bedrooms(self, param: int) -> str | None:
        """Get the bedrooms string for the url"""
        ...

    @abstractmethod
    def priceRange(self, param: list[int]) -> str | None:
        """Get the price range string for the url"""
        ...

    @abstractmethod
    def leaseDuration(self, param: int) -> str | None:
        """Get the lease duration string for the url"""
        ...

    @abstractmethod
    def leaseTerm(self, param: LeaseTerm) -> str | None:
        """Get the lease term sting for the url"""
        ...

    @abstractmethod
    def composeUrl(self, query: Query) -> dict[UrlFieldType, Any]:
        queryDict = query.getQueryParamDict();
        return {
            UrlFieldType.Prefix: None,
            UrlFieldType.PathPrefixes: [],
            UrlFieldType.Params: [
                *self.location(queryDict[QueryParam.Location]),
                self.reType(queryDict[QueryParam.REType]),
                self.bedrooms(queryDict[QueryParam.Bedrooms]),
                self.priceRange(queryDict[QueryParam.PriceRange]),
                self.leaseDuration(queryDict[QueryParam.LeaseDuration]),
                self.leaseTerm(queryDict[QueryParam.LeaseTerm])
            ]
        }

    def construct(self, query: Query):
        composedParams = self.composeUrl(query)
        prefix: str | None = composedParams[UrlFieldType.Prefix]
        pathPrefixes: list[str] = composedParams[UrlFieldType.PathPrefixes]
        params: list[str] = composedParams[UrlFieldType.Params]
        constructedUrl = self.baseUrl()
        if (prefix != None):
            splitUrl = constructedUrl.split('//')
            if (len(splitUrl) < 2):
                return None
            splitUrl.insert(1, '.')
            splitUrl.insert(1, prefix)
            constructedUrl = ""
            for part in splitUrl:
                constructedUrl += part
        if (pathPrefixes):
            for pathPrefix in pathPrefixes:
                constructedUrl += pathPrefix
                constructedUrl += '/'
        else:
            constructedUrl += '/'

        for param in params:
            constructedUrl += param
            constructedUrl += self.paramSeparator()

        if len(params) > 0:
            constructedUrl = constructedUrl[:-1]
            
        return constructedUrl