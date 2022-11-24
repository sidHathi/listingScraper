import sys
from UrlService import UrlService
from RentUrlService import RentUrlService
from Query import Query
from geopy.geocoders import Nominatim
from geopy.location import Location
from QueryParams import REType, LeaseTerm
from typing import cast
from Scrape import Scraper
from ParsingModel import ParsingModel
from TagModel import TagModel
from DBInterface import DBInterface
from Listing import Listing
from ListingService import ListingService
from RentListingService import RentListingService
from unitTests import testTagMapFollow, testRegexMatching
import asyncio

async def main() -> None:
    service: UrlService = RentUrlService()
    geolocator = Nominatim(user_agent='housing_scraper')
    geocoded = geolocator.geocode('Seattle, WA', exactly_one=True, addressdetails=True)
    if geocoded is None:
        raise Exception('invalid location')
    queryLoc = cast(Location, geocoded)
    if queryLoc is None or 'address' not in queryLoc.raw:
        raise Exception('location cast failed')

    query = Query(
        location=queryLoc,
        reType=REType.Apartment,
        bedrooms=1,
        priceRange=[0, 4000],
        leaseDuration=None,
        leaseTerm=LeaseTerm.ShortTerm
    )
    urlDict = service.composeUrl(query)
    print(urlDict)
    print (service.construct(query))

    tagModel = TagModel(identifiers={
        'data-tid': 'pdp-link', 
        'data-tag_item': 'property_title'
    })
    dbInterface = DBInterface()
    listingServce: ListingService = RentListingService()
    parsingModel = ParsingModel(targetTag=tagModel, requiresTagMap=False, listingService=listingServce)

    scraper = Scraper(
        urlString ='https://www.rent.com', 
        query=query,
        urlService=service, 
        listingService=listingServce,
        paginationModel=None, 
        parsingModel=parsingModel, 
        dbInterface = dbInterface
    )
    await scraper.searchHtmlPull(60)
    urls: list[str] = scraper.htmlParse()
    print(urls)
    await scraper.listingsHtmlPull(urls, 60)
    listings: list[Listing] = scraper.listingsScrape()
    print(listings)
    print(testTagMapFollow())
    print(testRegexMatching())

if (__name__ == '__main__'):
    sys.exit(asyncio.run(main()))