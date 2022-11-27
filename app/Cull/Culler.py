from ..models.CullingModel import CullingModel
from ..DBInterface import DBInterface
from ..scrapingUtils import htmlPull, followTagMap
from ..models.TagModel import TagModel

import asyncio
from datetime import datetime, timedelta
from typing import Coroutine, Any
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

class Culler:
    def __init__(self, cullingModel: CullingModel, dbInterface : DBInterface):
        self.cullingModel: CullingModel = cullingModel
        self.dbInterface: DBInterface = dbInterface

        self.dbUrlIdPairs: list[dict[str, Any]] | None = None

    def getDbUrls(self):
        self.dbUrlIdPairs = self.dbInterface.getListingUrls()

    async def checkListingIsExpired(self, url: str, browser: webdriver.Chrome, timeout: int = 60) -> bool:
        html: str = await htmlPull(url, browser, timeout)
        soup: BeautifulSoup = BeautifulSoup(html, 'html.parser')
        notFoundTag: TagModel = self.cullingModel.notFoundTag
        if soup.find(notFoundTag.tagType, notFoundTag.identifiers) is not None:
            return True

        statusTags: list[BeautifulSoup] = followTagMap(self.cullingModel.tagMap, soup)
        if len(statusTags) != 1:
            return False

        targetVal = self.cullingModel.targetVal
        if self.cullingModel.targetField is None:
            if targetVal in statusTags[0].text:
                return True
        else:
            if statusTags[0].get(self.cullingModel.targetField) == targetVal:
                return True
        return False

    async def cullExpiredListings(self):
        opts = ChromeOptions()
        browser = webdriver.Chrome('chromedriver', options=opts)
        browser.maximize_window()

        if self.dbUrlIdPairs is None:
            self.getDbUrls()
        assert self.dbUrlIdPairs is not None

        unexpiredPairs: list[dict[str, Any]] = []
        for pair in self.dbUrlIdPairs:
            assert 'scrapeTime' in pair
            currentTime = datetime.today()
            timeDif: timedelta = currentTime - pair['scrapeTime']
            if timeDif.days > self.cullingModel.expirationTimeInDays:
                assert '_id' in pair
                print(f'deleting {pair}')
                self.dbInterface.removeListing(pair['_id'])
            else:
                unexpiredPairs.append(pair)

        evaluators: list[Coroutine] = []
        for pair in unexpiredPairs:
            assert 'url' in pair
            evaluators.append(self.checkListingIsExpired(pair['url'], browser))
        
        expirationList: list[bool] = await asyncio.gather(*evaluators)
        for i in range(len(expirationList)):
            if expirationList[i]:
                culpritListingPair = self.dbUrlIdPairs[i]
                assert '_id' in culpritListingPair
                print(f'deleting {culpritListingPair}')
                self.dbInterface.removeListing(culpritListingPair['_id'])
