from bs4 import BeautifulSoup
from UrlService import UrlService
from Query import Query
from Listing import Listing
from PaginationModel import PaginationModel
from ParsingModel import ParsingModel, TagModel
from DBInterface import DBInterface
import requests
from collections.abc import Iterable
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

class Scraper:
    def __init__(self, 
        urlString: str, 
        urlService: UrlService,
        paginationModel: PaginationModel | None,
        parsingModel: ParsingModel,
        dbInterface: DBInterface ) -> None:
        self.urlString: str = urlString
        self.urlService: UrlService = urlService

        self.htmlObjects: list[BeautifulSoup] | None = None
        self.paginationModel: PaginationModel | None = paginationModel
        self.parsingModel: ParsingModel = parsingModel
        self.dbInterface: DBInterface = dbInterface

    def htmlPull(self, query: Query, timeout: int) -> None:
        '''
        TO-DO: Implement as per https://sidhathi.notion.site/Scraper-Planning-0fc4a6229b534d87b0e0241fd7d27905
        '''
        url = self.urlService.construct(query)
        if url is None:
            return
        
        opts = ChromeOptions()
        browser = webdriver.Chrome('chromedriver', options=opts)
        browser.maximize_window()
        browser.get(url)
        browser.implicitly_wait(timeout)
        baseHtml = browser.page_source
        soup = BeautifulSoup(baseHtml, 'html.parser')
        # ADD PAGINATION HERE

        print(soup.prettify())
        self.htmlObjects = [soup]
        return

    def htmlParse(self) -> list[str]:
        '''
        TO-DO: Implement as per https://sidhathi.notion.site/Scraper-Planning-0fc4a6229b534d87b0e0241fd7d27905
        '''
        if self.htmlObjects is None:
            return []

        def addTagAttrsToList(tags: Iterable[BeautifulSoup], list: list[str]):
            for tag in tags:
                url = tag.get(self.parsingModel.urlAttr)
                assert(url is not None)
                if type(url) is list:
                    url = url[0]
                assert(type(url) is str)
                if self.parsingModel.relativeHref:
                    url = self.urlString + url
                urls.append(url)
        
        urls = []
        targetTagName: str = self.parsingModel.targetTag.tagType
        targetTagIdentifiers: dict[str, str] = self.parsingModel.targetTag.identifiers
        for htmlObj in self.htmlObjects:
            if not self.parsingModel.requiresTagMap:
                tags = htmlObj.find_all(targetTagName, targetTagIdentifiers)
                addTagAttrsToList(tags, urls)
                continue
            tagMap = self.parsingModel.tagMap
            assert(tagMap is not None)
            currentTagList = []
            for step in tagMap:
                if len(currentTagList) < 1:
                    currentTagList = htmlObj.find_all(step.tagType, step.identifiers)
                    continue
                nextTagList = []
                for tag in currentTagList:
                    nextTagList.extend(tag.find_all(step.tagType, step.identifiers))
                currentTagList = nextTagList
            addTagAttrsToList(currentTagList, urls)

        return urls

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

