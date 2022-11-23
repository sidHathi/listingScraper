from ListingService import ListingService
from typing import Any, cast
from geopy.geocoders import Nominatim
from geopy.location import Location

class RentListingService(ListingService):
    def parseLocation(self, locStr: str) -> dict[str, Any]:
        geolocator = Nominatim(user_agent='housing_scraper')
        geocoded = geolocator.geocode(locStr, exactly_one=True, addressdetails=True)
        if geocoded is None:
            raise Exception('invalid location')
        location: Location = cast(Location, geocoded)
        if location is None or 'address' not in location.raw:
            raise Exception('location cast failed')
        return location.raw

    def parseBedroomOptions(self, opts: list[str]) -> list[int]:
        '''
        format {range Bed/Beds OR Studio}
        '''
        return super().parseBedroomOptions(opts)