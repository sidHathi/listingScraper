from bs4 import BeautifulSoup
import requests
from collections.abc import Iterable
import asyncio
from typing import Coroutine, Any, cast
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from undetected_chromedriver import Chrome as uChrome

from ..interfaces.UrlService import UrlService
from ..models.Query import Query
from ..models.Listing import Listing
from ..enums import ListingField
from ..constants import listingMap, fieldDefaults
from ..models.PaginationModel import PaginationModel
from ..models.ParsingModel import ParsingModel
from ..models.TagModel import TagModel
from ..DBInterface import DBInterface
from ..utils.scrapingUtils import htmlPull, followTagMap, queryToListingFieldConvert
from ..interfaces.ListingService import ListingService

class Scraper:
    def __init__(self, 
        urlString: str, 
        urlService: UrlService,
        listingService: ListingService,
        paginationModel: PaginationModel | None,
        parsingModel: ParsingModel,
        dbInterface: DBInterface ) -> None:
        self.urlString: str = urlString
        self.urlService: UrlService = urlService
        self.listingService: ListingService = listingService

        self.searchHtmlPages: list[BeautifulSoup] | None = None
        self.listingHtmlPages: dict[str, BeautifulSoup] | None = None
        self.paginationModel: PaginationModel | None = paginationModel
        self.parsingModel: ParsingModel = parsingModel
        self.dbInterface: DBInterface = dbInterface


    async def searchHtmlPull(self, query: Query, timeout: int) -> None:
        '''
        TO-DO: Implement pagination support as per 
        https://sidhathi.notion.site/Scraper-Planning-0fc4a6229b534d87b0e0241fd7d27905
        '''
        url = self.urlService.construct(query)
        if url is None:
            return
        opts = ChromeOptions()
        opts.add_argument("--window-size=1920,1080")
        browser = uChrome(options=opts)
        browser.maximize_window()
        
        baseHtml = await htmlPull(url, browser, timeout)
        # one retry for possible connection error
        if baseHtml is None:
            baseHtml = await htmlPull(url, browser, timeout)
        assert(baseHtml is not None)

        soup = BeautifulSoup(baseHtml, 'html.parser')
        # ADD PAGINATION HERE

        self.searchHtmlPages = [soup]
        browser.quit()
        return


    async def listingsHtmlPull(self, urls: list[str], timeout: int) -> None:
        opts = ChromeOptions()
        opts.add_argument("--window-size=1920,1080")
        browser = uChrome(options=opts)
        browser.maximize_window()

        urlIdPairs: list[dict[str, Any]] = self.dbInterface.getListingUrls()
        def getUrlFromPair(pair: dict[str, Any]):
            return pair['url']
        alreadyScraped: set[str] = set(list(map(getUrlFromPair, urlIdPairs)))

        concurrentScrapers: list[Coroutine] = []
        for url in urls:
            if url not in alreadyScraped:
                concurrentScrapers.append(htmlPull(url, browser, timeout))
        
        rawPages: list[str | None] = await asyncio.gather(*concurrentScrapers)
        def getSoup(page) -> BeautifulSoup:
            return BeautifulSoup(page, 'html.parser')
        filteredPages: list[str] = cast(list[str], filter(
            lambda page: page is not None,
            rawPages
        ))
        pages: list[BeautifulSoup] = list(map(getSoup, filteredPages))
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


    def listingsScrape(self, query: Query) -> list[Listing]:
        pages = self.listingHtmlPages
        assert(pages is not None)

        fieldMaps : dict[ListingField, list[TagModel] | None] = self.parsingModel.listingService.getFieldMaps()
        listings: list[Listing] = []
        for url, page in pages.items():
            listingJson: dict[str, Any] = {}
            listingJson[listingMap[ListingField.ProviderName]] = self.listingService.getProviderName()
            for field in ListingField:
                if field is ListingField.ProviderName:
                    continue
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
                    if queryVal is not None:
                        listingJson[listingMap[field]] = queryToListingFieldConvert(queryVal, field)
                        continue
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


    async def executeQuery(self, query: Query, timeout: int = 60) -> None:
        await self.searchHtmlPull(query, timeout)
        await self.listingsHtmlPull(self.htmlParse(), timeout)
        listings: list[Listing] = self.listingsScrape(query)

        for listing in listings:
            # print(listing)
            self.dbInterface.addListing(listing)

