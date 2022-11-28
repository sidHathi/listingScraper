import sys
import asyncio
from geopy.geocoders import Nominatim
from geopy.location import Location
from typing import cast

from ..interfaces.UrlService import UrlService
from ..Rent.RentUrlService import RentUrlService
from ..models.Query import Query
from ..enums import REType, LeaseTerm
from .Scraper import Scraper
from ..models.ParsingModel import ParsingModel
from ..models.TagModel import TagModel
from ..DBInterface import DBInterface
from ..models.Listing import Listing
from ..interfaces.ListingService import ListingService
from ..Rent.RentListingService import RentListingService
from ..FBM.FBMUrlService import FBMUrlService
from ..unitTests import testTagMapFollow, testRegexMatching
from ..constants import rentSearchingTag

async def main() -> None:
    service: UrlService = RentUrlService()
    fbService: UrlService = FBMUrlService()
    geolocator = Nominatim(user_agent='housing_scraper')
    geocoded = geolocator.geocode('Boston, MA', exactly_one=True, addressdetails=True)
    if geocoded is None:
        raise Exception('invalid location')
    queryLoc = cast(Location, geocoded)
    if queryLoc is None or 'address' not in queryLoc.raw:
        raise Exception('location cast failed')

    query = Query(
        location=queryLoc,
        reType=REType.Apartment,
        bedrooms=2,
        priceRange=[0, 3000],
        leaseDuration=None,
        leaseTerm=LeaseTerm.LongTerm,
        pets=True,
    )

    urlDict = service.composeUrl(query)
    fbUrlDict = fbService.composeUrl(query)
    print(fbUrlDict)
    print(fbService.construct(query))
    print(urlDict)
    print (service.construct(query))

    dbInterface = DBInterface()
    listingServce: ListingService = RentListingService()
    parsingModel = ParsingModel(targetTag=rentSearchingTag, requiresTagMap=False, listingService=listingServce)

    scraper = Scraper(
        urlString ='https://www.rent.com', 
        query=query,
        urlService=service, 
        listingService=listingServce,
        paginationModel=None, 
        parsingModel=parsingModel, 
        dbInterface = dbInterface
    )
    await scraper.executeQuery(query)
    # await scraper.searchHtmlPull(60)
    # urls: list[str] = scraper.htmlParse()
    # print(urls)
    # await scraper.listingsHtmlPull(urls, 60)
    # listings: list[Listing] = scraper.listingsScrape()
    # print(listings)
    # print(testTagMapFollow())
    # print(testRegexMatching())

if (__name__ == '__main__'):
    sys.exit(asyncio.run(main()))