import asyncio

from .QueryReader import QueryReader
from .Scraper import Scraper
from ..DBInterface import DBInterface
from ..models.Query import Query
from ..interfaces.UrlService import UrlService
from ..interfaces.ListingService import ListingService
from ..models.ParsingModel import ParsingModel
from ..constants import rentSearchingTag, fbmSearchingTag

from ..FBM.FBMListingService import FBMListingService
from ..FBM.FBMUrlService import FBMUrlService
from ..Rent.RentListingService import RentListingService
from ..Rent.RentUrlService import RentUrlService

class App:
    def __init__(self, dbInterface: DBInterface):
        self.dbInterface: DBInterface = dbInterface

    def getQueries(self) -> list[Query]:
        reader: QueryReader = QueryReader(self.dbInterface)

        return reader.getQueryList()

    def buildScrapers(self) -> list[Scraper]:
        rentUrlService: UrlService = RentUrlService()
        rentListingService: ListingService = RentListingService()
        rentParsingModel = ParsingModel(targetTag=rentSearchingTag, requiresTagMap=False, listingService=rentListingService)
        rentScraper: Scraper = Scraper(
            urlString ='https://www.rent.com', 
            urlService=rentUrlService, 
            listingService=rentListingService,
            paginationModel=None, 
            parsingModel=rentParsingModel, 
            dbInterface = self.dbInterface
        )

        fbmUrlService: UrlService = FBMUrlService()
        fbmListingService: ListingService = FBMListingService()
        fbmParsingModel = ParsingModel(targetTag=fbmSearchingTag, requiresTagMap=False, listingService=fbmListingService)
        fbmScraper: Scraper = Scraper(
            urlString ='https://www.facebook.com', 
            urlService=fbmUrlService, 
            listingService=fbmListingService,
            paginationModel=None, 
            parsingModel=fbmParsingModel, 
            dbInterface = self.dbInterface
        )

        return [rentScraper, fbmScraper]

    async def run(self):
        queries: list[Query] = self.getQueries()
        print(queries)
        scrapers: list[Scraper] = self.buildScrapers()

        for query in queries:
            for scraper in scrapers:
                await scraper.executeQuery(query)