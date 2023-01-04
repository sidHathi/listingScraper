from .QueryReader import QueryReader
from .Scraper import Scraper
from ..DBInterface import DBInterface
from ..RequestHub import RequestHub
from ..models.Query import Query
from ..interfaces.UrlService import UrlService
from ..interfaces.ListingService import ListingService
from ..models.ParsingModel import ParsingModel
from ..constants import rentSearchingTag, fbmSearchingTag, zillowSearchingTag, apartmentsSearchingTag

from ..FBM.FBMListingService import FBMListingService
from ..FBM.FBMUrlService import FBMUrlService
from ..Rent.RentListingService import RentListingService
from ..Rent.RentUrlService import RentUrlService
from ..Zillow.ZillowListingService import ZillowListingService
from ..Zillow.ZillowUrlService import ZillowUrlService
from ..Apartments.ApartmentsListingService import ApartmentsListingService
from ..Apartments.ApartmentsUrlService import ApartmentsUrlService

class App:
    def __init__(self, dbInterface: DBInterface, requestHub: RequestHub):
        self.dbInterface: DBInterface = dbInterface
        self.requestHub: RequestHub = requestHub

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
            dbInterface = self.dbInterface, 
            requestHub=self.requestHub,
            scrapeWithProxy=False,
            scrapeHeadlessly=False
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
            dbInterface = self.dbInterface, 
            requestHub=self.requestHub,
            scrapeWithProxy=True,
            scrapeHeadlessly=True
        )

        zillowUrlService: UrlService = ZillowUrlService()
        zillowListingService: ListingService = ZillowListingService()
        zillowParsingModel = ParsingModel(targetTag=zillowSearchingTag, requiresTagMap=False, listingService=zillowListingService)
        zillowScraper: Scraper = Scraper(
            urlString ='', 
            urlService=zillowUrlService, 
            listingService=zillowListingService,
            paginationModel=None, 
            parsingModel=zillowParsingModel, 
            dbInterface = self.dbInterface, 
            requestHub=self.requestHub,
            scrapeWithProxy=True,
            scrapeHeadlessly=False
        )

        apartmentsUrlService: UrlService = ApartmentsUrlService()
        apartmentsListingService: ListingService = ApartmentsListingService()
        apartmentsParsingModel = ParsingModel(targetTag=apartmentsSearchingTag, requiresTagMap=False, listingService=apartmentsListingService)
        apartmentsScraper: Scraper = Scraper(
            urlString ='', 
            urlService=apartmentsUrlService, 
            listingService=apartmentsListingService,
            paginationModel=None, 
            parsingModel=apartmentsParsingModel, 
            dbInterface = self.dbInterface, 
            requestHub=self.requestHub,
            scrapeWithProxy=False,
            scrapeHeadlessly=False
        )

        return [apartmentsScraper, zillowScraper, fbmScraper, rentScraper]

    async def run(self):
        queries: list[Query] = self.getQueries()
        print(queries)
        scrapers: list[Scraper] = self.buildScrapers()

        for query in queries:
            for scraper in scrapers:
                scraper.executeQuery(query)