import sys
from UrlService import UrlService
from RentUrlService import RentUrlService
from Query import Query
from geopy.geocoders import Nominatim
from geopy.location import Location
from QueryParams import REType, LeaseTerm
from typing import cast
from Scrape import Scraper
from ParsingModel import ParsingModel, TagModel
from DBInterface import DBInterface
import asyncio

async def main() -> None:
    service: UrlService = RentUrlService()
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
        bedrooms=1,
        priceRange=[0, 3000],
        leaseDuration=0,
        leaseTerm=LeaseTerm.LongTerm
    )
    urlDict = service.composeUrl(query)
    print(urlDict)
    print (service.construct(query))

    tagModel = TagModel(identifiers={
        'data-tid': 'pdp-link', 
        'data-tag_item': 'property_title'
    })
    parsingModel = ParsingModel(targetTag=tagModel, requiresTagMap=False, listingFieldMaps={})
    dbInterface = DBInterface()
    scraper = Scraper(
        urlString ='https://www.rent.com', 
        urlService=service, 
        paginationModel=None, 
        parsingModel=parsingModel, 
        dbInterface = dbInterface
    )
    await scraper.searchHtmlPull(query, 60)
    urls: list[str] = scraper.htmlParse()
    print(urls)
    await scraper.listingsScrape(urls, 60)
    

if (__name__ == '__main__'):
    sys.exit(asyncio.run(main()))