from ..models.CullingModel import CullingModel
from ..DBInterface import DBInterface
from ..utils.scrapingUtils import htmlPull, followTagMap
from ..models.TagModel import TagModel
from ..RequestHub import RequestHub

import asyncio
from datetime import datetime, timedelta
from typing import Coroutine, Any
from bs4 import BeautifulSoup
from undetected_chromedriver import Chrome as uChrome
from selenium.webdriver.chrome.options import Options as ChromeOptions

class Culler:
    def __init__(self, cullingModels: dict[str, CullingModel], dbInterface : DBInterface, requestHub: RequestHub):
        self.cullingModels: dict[str, CullingModel] = cullingModels
        self.dbInterface: DBInterface = dbInterface
        self.requestHub = requestHub

        self.dbUrlNamePairs: list[dict[str, Any]] | None = None

    def getDbUrls(self):
        self.dbUrlNamePairs = self.dbInterface.getListingUrlsByProvider()

    def checkListingIsExpired(self, provider: str, url: str) -> bool:
        # one retry for possible connection error
        html: str | None = self.requestHub.executeRequest(
            url=url,
            elemOnSuccess=self.cullingModels[provider].elemOnPageLoad
        )
        if html is None:
            return True

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

    async def cullExpiredListings(self):
        if self.dbUrlNamePairs is None:
            self.getDbUrls()
        assert self.dbUrlNamePairs is not None

        unexpiredPairs: list[dict[str, Any]] = []
        for pair in self.dbUrlNamePairs:
            assert 'scrapeTime' in pair
            assert 'providerName' in pair
            provider = pair['providerName']
            currentTime = datetime.today()
            timeDif: timedelta = currentTime - pair['scrapeTime']
            if timeDif.days > self.cullingModels[provider].expirationTimeInDays:
                assert '_id' in pair
                print(f'deleting {pair}')
                self.dbInterface.removeListing(pair['_id'])
            else:
                unexpiredPairs.append(pair)

        cullList: list[bool] = []
        for pair in unexpiredPairs:
            assert 'url' in pair
            assert 'providerName' in pair
            cullList.append(self.checkListingIsExpired(pair['providerName'], pair['url']))
        
        for i in range(len(cullList)):
            if cullList[i]:
                culpritListingPair = self.dbUrlNamePairs[i]
                assert '_id' in culpritListingPair
                print(f'deleting {culpritListingPair}')
                self.dbInterface.removeListing(culpritListingPair['_id'])
