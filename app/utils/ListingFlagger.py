from typing import Any

from ..models.Listing import Listing

class ListingFlagger:
    # flagging functions return true for bad values
    def checkValidPrice(self, price: int) -> bool:
        if price < 100 or price > 20000:
            print('invalid price')
            return False
        return True
    
    def checkValidBedrooms(self, bedrooms: list[int]) -> bool:
        if len(bedrooms) < 2 or bedrooms[0] > 20 or bedrooms[1] > 20 or bedrooms[0] > bedrooms[1]:
            print('invalid bedrooms')
            return False
        return True
    
    def checkValidLeaseTerm(self, leaseTerm: int) -> bool:
        if leaseTerm < 0 or leaseTerm > 48:
            print('invalid lease term')
            return False
        return True
    
    def checkValidListing(self, rawListing: dict[str, Any]) -> bool:
        if 'price' not in rawListing or 'bedrooms' not in rawListing or 'shortestLease' not in rawListing:
            print('key missing for listing')
            return False
        if not self.checkValidPrice(rawListing['price']) or not self.checkValidBedrooms(rawListing['bedrooms']) or not self.checkValidLeaseTerm(rawListing['shortestLease']):
            return False
        return True