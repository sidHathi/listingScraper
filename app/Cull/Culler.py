import asyncio
from datetime import datetime, timedelta
from typing import Coroutine, Any
from bs4 import BeautifulSoup
from undetected_chromedriver import Chrome as uChrome
from selenium.webdriver.chrome.options import Options as ChromeOptions

from ..models.CullingModel import CullingModel
from ..DBInterface import DBInterface
from ..utils.scrapingUtils import htmlPull, followTagMap
from ..models.TagModel import TagModel
from ..models.Listing import Listing
from ..RequestHub import RequestHub
from ..utils.ListingFlagger import ListingFlagger

expirationTimeInDays = 10

class Culler:
    def __init__(self, cullingModels: dict[str, CullingModel], dbInterface : DBInterface, requestHub: RequestHub):
        self.cullingModels: dict[str, CullingModel] = cullingModels
        self.dbInterface: DBInterface = dbInterface
        self.requestHub = requestHub

        self.rawListings: list[dict[str, Any]] | None = None
        self.listingFlagger: ListingFlagger = ListingFlagger()

    def getListings(self):
        self.rawListings = self.dbInterface.getListingsCullingInfo()

    def checkListingIsExpired(self, provider: str, url: str) -> bool:
        if provider in self.cullingModels:
            # one retry for possible connection error
            html: str | None = self.requestHub.executeRequest(
                url=url,
                elemOnSuccess=self.cullingModels[provider].elemOnPageLoad,
                proxy=False # no proxy use to conserve data throughput
            )
            if html is None:
                return False
            soup: BeautifulSoup = BeautifulSoup(html, 'html.parser')
            notFoundTag: TagModel | None = self.cullingModels[provider].notFoundTag

            if notFoundTag is not None and soup.find(notFoundTag.tagType, notFoundTag.identifiers) is not None:
                return True
            statusTags: list[BeautifulSoup] = followTagMap(self.cullingModels[provider].tagMap, soup)
            if len(statusTags) != 1:
                return False

            targetVal = self.cullingModels[provider].targetVal
            targetField = self.cullingModels[provider].targetField
            if targetField is None:
                if targetVal in statusTags[0].text:
                    return True
            else:
                if statusTags[0].get(targetField) == targetVal:
                    return True
        return False

    async def cullListings(self):
        if self.rawListings is None:
            self.getListings()
        assert self.rawListings is not None

        unexpiredPairs: list[dict[str, Any]] = []
        for raw in self.rawListings:
            assert 'scrapeTime' in raw
            assert 'providerName' in raw
            assert 'price' in raw
            # provider = pair['providerName']
            currentTime = datetime.today()
            timeDif: timedelta = currentTime - raw['scrapeTime']
            if timeDif.days > expirationTimeInDays or not self.listingFlagger.checkValidListing(raw):
                assert '_id' in raw
                print(f'deleting {raw}')
                self.dbInterface.removeListing(raw['_id'])
            else:
                unexpiredPairs.append(raw)

        cullList: list[bool] = []
        for pair in unexpiredPairs:
            assert 'url' in pair
            assert 'providerName' in pair
            cullList.append(self.checkListingIsExpired(pair['providerName'], pair['url']))
        
        for i in range(len(cullList)):
            if cullList[i]:
                culpritListing = self.rawListings[i]
                assert '_id' in culpritListing
                print(f'deleting {culpritListing}')
                self.dbInterface.removeListing(culpritListing['_id'])
