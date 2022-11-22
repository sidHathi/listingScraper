from bs4 import BeautifulSoup
from UrlService import UrlService
from Query import Query
from Listing import Listing
from PaginationModel import PaginationModel
from ParsingModel import ParsingModel
from DBInterface import DBInterface

class Scraper:
    def __init__(self, 
        urlString: str, 
        urlService: UrlService,
        paginationModel: PaginationModel,
        parsingModel: ParsingModel,
        dbInterface: DBInterface ) -> None:
        self.urlString: str = urlString
        self.urlService: UrlService = urlService

        self.htmlObject: list[BeautifulSoup] | None = None
        self.paginationModel: PaginationModel = paginationModel
        self.parsingModel: ParsingModel = parsingModel
        self.dbInterface: DBInterface = dbInterface

    def htmlPull(self, query: Query) -> None:
        '''
        TO-DO: Implement as per https://sidhathi.notion.site/Scraper-Planning-0fc4a6229b534d87b0e0241fd7d27905
        '''
        return

    def htmlParse(self) -> list[str]:
        '''
        TO-DO: Implement as per https://sidhathi.notion.site/Scraper-Planning-0fc4a6229b534d87b0e0241fd7d27905
        '''
        return []

    def listingsScrape(self, listings: list[str]) -> list[Listing]:
        '''
        TO-DO: Implement as per https://sidhathi.notion.site/Scraper-Planning-0fc4a6229b534d87b0e0241fd7d27905
        '''
        return []

    def executeQuery(self, query: Query) -> None:
        '''
        TO-DO: Implement as per https://sidhathi.notion.site/Scraper-Planning-0fc4a6229b534d87b0e0241fd7d27905
        '''
        return

