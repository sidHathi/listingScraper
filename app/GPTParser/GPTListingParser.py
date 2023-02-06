from typing import Any

from .gptUtils import parseRentalListing
from..utils.scrapingUtils import findPrice

class GPTListingParser:
    def __init__(self, providerName: str) -> None:
        self.providerName = providerName

        self.listing: dict[str, Any] | None = None

    def parse(self, pageText: str):
        gptResponse: dict[str, str] | None = parseRentalListing(self.providerName, pageText)
        self.listing = gptResponse

    def getPrice(self) -> int | None:
        if self.listing is None or 'price' not in self.listing:
            return None
        
        priceStr = findPrice(self.listing['price'])
        if priceStr is None:
            return None
        return int(priceStr)
    
    def getBedrooms(self) -> int | None:
        if self.listing is None or 'bedrooms' not in self.listing:
            return None
        
        return int(self.listing['bedrooms'])
    
    def getLeaseDuration(self) -> int | None:
        if self.listing is None or 'leaseDuration' not in self.listing:
            return None
        
        return int(self.listing['leaseDuration'])
    
    def getAddress(self) -> str | None:
        if self.listing is None or 'address' not in self.listing:
            return None
        
        return self.listing['address']
        

