from geopy.location import Location
from geopy.distance import geodesic as GD
from pyqtree import Index
import math
import functools

'''
The following four utility functions are from: 
https://stackoverflow.com/questions/238260/how-to-calculate-the-bounding-box-for-a-given-lat-lng-location
'''
# degrees to radians
def deg2rad(degrees):
    return math.pi*degrees/180.0
# radians to degrees
def rad2deg(radians):
    return 180.0*radians/math.pi

# Semi-axes of WGS-84 geoidal reference
WGS84_a = 6378137.0  # Major semiaxis [m]
WGS84_b = 6356752.3  # Minor semiaxis [m]

# Earth radius at a given latitude, according to the WGS-84 ellipsoid [m]
def WGS84EarthRadius(lat):
    # http://en.wikipedia.org/wiki/Earth_radius
    An = WGS84_a*WGS84_a * math.cos(lat)
    Bn = WGS84_b*WGS84_b * math.sin(lat)
    Ad = WGS84_a * math.cos(lat)
    Bd = WGS84_b * math.sin(lat)
    return math.sqrt( (An*An + Bn*Bn)/(Ad*Ad + Bd*Bd) )

# Bounding box surrounding the point at given coordinates,
# assuming local approximation of Earth surface as a sphere
# of radius given by WGS84
def boundingBox(latitudeInDegrees, longitudeInDegrees, halfSideInKm):
    lat = deg2rad(latitudeInDegrees)
    lon = deg2rad(longitudeInDegrees)
    halfSide = 1000*halfSideInKm

    # Radius of Earth at given latitude
    radius = WGS84EarthRadius(lat)
    # Radius of the parallel at given latitude
    pradius = radius*math.cos(lat)

    latMin = lat - halfSide/radius
    latMax = lat + halfSide/radius
    lonMin = lon - halfSide/pradius
    lonMax = lon + halfSide/pradius

    return (rad2deg(latMin), rad2deg(lonMin), rad2deg(latMax), rad2deg(lonMax))

# quad tree search class for searching locations
class LocationQTree:
    def __init__(self, initialPoints: list[Location] | None = None):
        self.qTree = Index(bbox=(-180, -90, 180, 90))
        if initialPoints is not None:
            self.construct(initialPoints)

    def insert(self, newPoint: Location):
        self.qTree.insert(newPoint, bbox=boundingBox(newPoint.latitude, newPoint.longitude, 1))

    def construct(self, newPoints: list[Location]):
        for point in newPoints:
            self.insert(point)

    def getNearestLoc(self, searchPoint: Location, boundInKm: int) -> Location | None:
        intersect: list[Location] = self.qTree.intersect(boundingBox(searchPoint.latitude, searchPoint.longitude, boundInKm))
        if len(intersect) == 0:
            return None
        def dist(loc1: Location, loc2: Location):
            return GD((loc1.latitude, loc1.longitude), (loc2.latitude, loc2.longitude))
        sortedIntersect: list[Location] = sorted(intersect, key=lambda loc: dist(loc, searchPoint))
        return sortedIntersect[0]