from bs4 import BeautifulSoup
from ..interfaces.UrlService import UrlService
from ..models.Query import Query
from ..models.Listing import Listing
from ..enums import ListingField
from ..constants import listingMap, fieldDefaults
from ..models.PaginationModel import PaginationModel
from ..models.ParsingModel import ParsingModel
from ..models.TagModel import TagModel
from ..DBInterface import DBInterface
import requests
from collections.abc import Iterable
import asyncio
from typing import Coroutine, Any
from ..scrapingUtils import htmlPull, followTagMap
from ..interfaces.ListingService import ListingService
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
        self.listingHtmlPages: dict[str, BeautifulSoup] | None = None
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

        self.searchHtmlPages = [soup]
        browser.quit()
        return


    async def listingsHtmlPull(self, urls: list[str], timeout: int) -> None:
        opts = ChromeOptions()
        browser = webdriver.Chrome('chromedriver', options=opts)
        browser.maximize_window()

        urlIdPairs: list[dict[str, Any]] = self.dbInterface.getListingUrls()
        def getUrlFromPair(pair: dict[str, Any]):
            return pair['url']
        alreadyScraped: set[str] = set(list(map(getUrlFromPair, urlIdPairs)))

        concurrentScrapers: list[Coroutine] = []
        for url in urls:
            if url not in alreadyScraped:
                concurrentScrapers.append(htmlPull(url, browser, timeout))
        
        rawPages = await asyncio.gather(*concurrentScrapers)
        def getSoup(page) -> BeautifulSoup:
            return BeautifulSoup(page, 'html.parser')
        pages: list[BeautifulSoup] = list(map(getSoup, rawPages))
        browser.quit()
        self.listingHtmlPages = dict(zip(urls, pages))


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
        query = self.query
        pages = self.listingHtmlPages
        assert(pages is not None)

        fieldMaps : dict[ListingField, list[TagModel] | None] = self.parsingModel.listingService.getFieldMaps()
        listings: list[Listing] = []
        for url, page in pages.items():
            listingJson: dict[str, Any] = {}
            for field in ListingField:
                if field == ListingField.Url:
                    listingJson[listingMap[field]] = url
                    continue
                fieldMap: list[TagModel] | None = fieldMaps[field]
                qField = query.getCorrespondingParam(field)
                if qField is None:
                    queryVal = None
                else:
                    queryVal = query.getQueryParamDict()[qField]
                if fieldMap is None:
                     assert(queryVal is not None)
                     listingJson[listingMap[field]] = queryVal
                     continue
                matchingTags = followTagMap(fieldMap, page)
                if len(matchingTags) < 1:
                    listingJson[listingMap[field]] = fieldDefaults[field]
                    continue
                matchedTag = matchingTags[0]
                specialField = self.listingService.getSpecialFieldName(field)
                if specialField is None:
                    valStr = matchedTag.text
                else:
                    valStr = matchedTag.get(specialField)
                    assert(valStr is not None and type(valStr) == 'str')
                val = self.listingService.parse(field, str(valStr), queryVal)
                listingJson[listingMap[field]] = val
            listing = Listing(**listingJson)
            listings.append(listing)
        return listings


    async def executeQuery(self, query: Query | None = None, timeout: int = 60) -> None:
        if query is not None:
            self.query = query
        await self.searchHtmlPull(timeout)
        await self.listingsHtmlPull(self.htmlParse(), timeout)
        listings: list[Listing] = self.listingsScrape()

        for listing in listings:
            self.dbInterface.addListing(listing)

