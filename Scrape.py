from bs4 import BeautifulSoup
from UrlService import UrlService
from Query import Query
from Listing import Listing, ListingField, ListingMap
from PaginationModel import PaginationModel
from ParsingModel import ParsingModel, TagModel
from DBInterface import DBInterface
import requests
from collections.abc import Iterable
import asyncio
from typing import Coroutine, Any
from ScrapingUtils import htmlPull, followTagMap
from ListingService import ListingService

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
        
        baseHtml = await htmlPull(url, timeout)
        soup = BeautifulSoup(baseHtml, 'html.parser')
        # ADD PAGINATION HERE

        print(soup.prettify())
        self.searchHtmlPages = [soup]
        return

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
        targetTagName: str = self.parsingModel.targetTag.tagType
        targetTagIdentifiers: dict[str, str] = self.parsingModel.targetTag.identifiers
        for htmlObj in self.searchHtmlPages:
            if not self.parsingModel.requiresTagMap:
                tags = htmlObj.find_all(targetTagName, targetTagIdentifiers)
                addTagAttrsToList(tags, urls)
                continue
            tagMap = self.parsingModel.tagMap
            assert(tagMap is not None)
            tags: list[BeautifulSoup] = followTagMap(tagMap=tagMap, dom=htmlObj)
            addTagAttrsToList(tags, urls)

        return urls

    async def listingsScrape(self, urls: list[str], timeout: int) -> list[Listing]:
        '''
        TO-DO: Implement as per https://sidhathi.notion.site/Scraper-Planning-0fc4a6229b534d87b0e0241fd7d27905
        '''
        concurrentScrapers: list[Coroutine] = []
        for url in urls:
            concurrentScrapers.append(htmlPull(url, timeout))
        
        rawPages = await asyncio.gather(*concurrentScrapers)
        def getSoup(page) -> BeautifulSoup:
            return BeautifulSoup(page, 'html.parser')
        pages: list[BeautifulSoup] = list(map(getSoup, rawPages))

        fieldMaps : dict[ListingField, list[TagModel]] = self.parsingModel.listingFieldMaps
        listings: list[Listing] = []
        for page in pages:
            listingJson: dict[str, Any] = {}
            for field in ListingField:
                fieldMap: list[TagModel] = fieldMaps[field]
                matchingTags = followTagMap(fieldMap, page)
                assert(len(matchingTags) == 1)
                matchedTag = matchingTags[0]
                specialField = self.listingService.getSpecialFieldName(field)
                if specialField is None:
                    valStr = matchedTag.text
                    val = self.listingService.parse(field, valStr)
                    listingJson[ListingMap[field]] = val
                else:
                    valStr = matchedTag.get(specialField)
                    assert(matchedTag is not None and type(valStr) == 'str')
                    val = self.listingService.parse(field, str(valStr))
                    listingJson[ListingMap[field]] = val
            listing = Listing(**listingJson)
            listings.append(listing)
        return listings

    def executeQuery(self, query: Query) -> None:
        '''
        TO-DO: Implement as per https://sidhathi.notion.site/Scraper-Planning-0fc4a6229b534d87b0e0241fd7d27905
        '''
        return

