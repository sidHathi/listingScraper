from geopy.geocoders import Nominatim
from geopy.location import Location
from typing import cast

from ..utils.locationUtils import LocationQTree
from ..utils.locationUtils import LocationQTree

validLocations: set[str] = {
    'boston',
    'new york',
    'seattle',
    'los angeles',
    'san francisco',
    'san jose',
    'philadelphia',
    'washington dc',
    'portland',
    'chicago',
    'houston',
    'phoenix',
    'san antonio',
    'san diego',
    'dallas',
    'austin',
    'jacksonville',
    'fort worth',
    'columbus',
    'charlotte',
    'indianapolis',
    'denver',
}

locationStates = {
    'boston': "MA",
    'new york': "NY",
    'seattle': "WA",
    'los angeles': "CA",
    'san francisco': "CA",
    'san jose': "CA",
    'philadelphia': "PA",
    'washington dc': "",
    'portland': "OR",
    'chicago': "IL",
    'houston': "TX",
    'phoenix': "AZ",
    'san antonio': "TX",
    'san diego': "CA",
    'dallas': "TX",
    'austin': "TX",
    'jacksonville': "FL",
    'fort worth': "TX",
    'columbus': "OH",
    'charlotte': "NC",
    'indianapolis': "IN",
    'denver': "CO",
}

shortenedLocations: dict[str, str] = {
    'los angeles': 'la',
    'washington': 'dc',
    'city of new york': 'nyc'
}

fbGeolocator = Nominatim(user_agent='housing_scraper')
quadTree: LocationQTree = LocationQTree([
    cast(Location, fbGeolocator.geocode(f"{locationStr}, {locationStates[locationStr]}", exactly_one=True, addressdetails=True)) for locationStr in validLocations
])

searchResultsMaxDist: int = 100