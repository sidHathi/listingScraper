from bs4 import BeautifulSoup
from UrlService import UrlService
from Query import Query
from Listing import Listing, ListingField, ListingMap
from PaginationModel import PaginationModel
from ParsingModel import ParsingModel
from TagModel import TagModel
from DBInterface import DBInterface
import requests
from collections.abc import Iterable
import asyncio
from typing import Coroutine, Any
from scrapingUtils import htmlPull, followTagMap
from ListingService import ListingService
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions


class Scraper:
    def __init__(self, 
        urlString: str, 
        query: Query,
        urlService: UrlService,
        listingService: ListingService,
        paginationModel: PaginationModel | None,
        parsingModel: ParsingModel,
        dbInterface: DBInterface ) -> None:
        self.urlString: str = urlString
        self.query = query
        self.urlService: UrlService = urlService
        self.listingService: ListingService = listingService

        self.searchHtmlPages: list[BeautifulSoup] | None = None
        self.listingHtmlPages: list[BeautifulSoup] | None = None
        self.paginationModel: PaginationModel | None = paginationModel
        self.parsingModel: ParsingModel = parsingModel
        self.dbInterface: DBInterface = dbInterface


    async def searchHtmlPull(self, timeout: int) -> None:
        '''
        TO-DO: Implement pagination support as per 
        https://sidhathi.notion.site/Scraper-Planning-0fc4a6229b534d87b0e0241fd7d27905
        '''
        url = self.urlService.construct(self.query)
        if url is None:
            return
        opts = ChromeOptions()
        browser = webdriver.Chrome('chromedriver', options=opts)
        browser.maximize_window()
        
        baseHtml = await htmlPull(url, browser, timeout)
        soup = BeautifulSoup(baseHtml, 'html.parser')
        # ADD PAGINATION HERE

        print(soup.prettify())
        self.searchHtmlPages = [soup]
        browser.quit()
        return


    async def listingsHtmlPull(self, urls: list[str], timeout: int) -> None:
        opts = ChromeOptions()
        browser = webdriver.Chrome('chromedriver', options=opts)
        browser.maximize_window()

        concurrentScrapers: list[Coroutine] = []
        for url in urls:
            concurrentScrapers.append(htmlPull(url, browser, timeout))
        
        rawPages = await asyncio.gather(*concurrentScrapers)
        def getSoup(page) -> BeautifulSoup:
            return BeautifulSoup(page, 'html.parser')
        pages: list[BeautifulSoup] = list(map(getSoup, rawPages))
        browser.quit()
        self.listingHtmlPages = pages


    def htmlParse(self) -> list[str]:
        '''
        Interprets the ParsingModel to extract a list of listing urls
        from a search results url
        '''
        if self.searchHtmlPages is None:
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
        targetTagName: str | None = self.parsingModel.targetTag.tagType
        targetTagIdentifiers: dict[str, str] = self.parsingModel.targetTag.identifiers
        for htmlObj in self.searchHtmlPages:
            if not self.parsingModel.requiresTagMap:
                tags = htmlObj.find_all(name=targetTagName, attrs=targetTagIdentifiers)
                addTagAttrsToList(tags, urls)
                continue
            tagMap = self.parsingModel.tagMap
            assert(tagMap is not None)
            tags: list[BeautifulSoup] = followTagMap(tagMap=tagMap, dom=htmlObj)
            addTagAttrsToList(tags, urls)

        return urls


    def listingsScrape(self) -> list[Listing]:
        '''
        TO-DO: Implement as per https://sidhathi.notion.site/Scraper-Planning-0fc4a6229b534d87b0e0241fd7d27905
        '''
        query = self.query
        pages = self.listingHtmlPages
        assert(pages is not None)

        fieldMaps : dict[ListingField, list[TagModel] | None] = self.parsingModel.listingService.getFieldMaps()
        listings: list[Listing] = []
        for page in pages:
            listingJson: dict[str, Any] = {}
            for field in ListingField:
                fieldMap: list[TagModel] | None = fieldMaps[field]
                qField = query.getCorrespondingParam(field)
                if qField is None:
                    queryVal = None
                else:
                    queryVal = query.getQueryParamDict()[qField]
                if fieldMap is None:
                     assert(queryVal is not None)
                     listingJson[ListingMap[field]] = queryVal
                     continue
                matchingTags = followTagMap(fieldMap, page)
                print(fieldMap)
                print(len(matchingTags))
                assert(len(matchingTags) == 1)
                matchedTag = matchingTags[0]
                specialField = self.listingService.getSpecialFieldName(field)
                if specialField is None:
                    valStr = matchedTag.text
                else:
                    valStr = matchedTag.get(specialField)
                    assert(valStr is not None and type(valStr) == 'str')
                val = self.listingService.parse(field, str(valStr), queryVal)
                listingJson[ListingMap[field]] = val
            listing = Listing(**listingJson)
            listings.append(listing)
        return listings


    def executeQuery(self, query: Query) -> None:
        '''
        TO-DO: Implement as per https://sidhathi.notion.site/Scraper-Planning-0fc4a6229b534d87b0e0241fd7d27905
        '''
        return

