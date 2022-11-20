from pydantic import BaseModel
from geopy.geocoders import Nominatim
from geopy.location import Location

class Query(BaseModel):
    location: Location