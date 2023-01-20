from datetime import datetime

from .models.ScrapeMetrics import ScrapeMetrics
from .models.EventMetric import EventMetric
from ..DBInterface import DBInterface

class MetricsController:
    '''
    Each metrics controller should be specific to a given scraping
    instance. It's job is to provide an easy interface to record each event
    that occurs during a scrape and store it in a ScrapeMetrics model
    '''
    def __init__(self, dbInterface: DBInterface):
        self.scrapeMetrics: ScrapeMetrics = ScrapeMetrics(
            timestamp=datetime.now(),
            allScrapes=EventMetric(),
            scrapesByDomain={},
            scrapesByProxyUsage={},
            scrapesByLocation={},
            suspectParsesByDomain={},
            totalFailures=0,
            failuresByType={},
            fubarEvents=[]
        )
        self.dbInterface = dbInterface
        self.currentScrapingLocName: str = "unknown"

    def setCurrentScrapingLocName(self, locName: str):
        self.currentScrapingLocName = locName

    def logSuccess(self, domain: str, proxy: bool):
        self.scrapeMetrics.allScrapes.addSuccess()
        if domain not in self.scrapeMetrics.scrapesByDomain:
            self.scrapeMetrics.scrapesByDomain[domain] = EventMetric()
        self.scrapeMetrics.scrapesByDomain[domain].addSuccess()

        proxyStr: str = 'true' if proxy else 'false'
        if proxyStr not in self.scrapeMetrics.scrapesByProxyUsage:
            self.scrapeMetrics.scrapesByProxyUsage[proxyStr] = EventMetric()
        self.scrapeMetrics.scrapesByProxyUsage[proxyStr].addSuccess()
        
        if self.currentScrapingLocName not in self.scrapeMetrics.scrapesByLocation:
            self.scrapeMetrics.scrapesByLocation[self.currentScrapingLocName] = EventMetric()
        self.scrapeMetrics.scrapesByLocation[self.currentScrapingLocName].addSuccess()
        
    def logFailure(self, domain: str, proxy: bool, type: str):
        self.scrapeMetrics.allScrapes.addFailure()
        if domain not in self.scrapeMetrics.scrapesByDomain:
            self.scrapeMetrics.scrapesByDomain[domain] = EventMetric()
        self.scrapeMetrics.scrapesByDomain[domain].addFailure()

        proxyStr: str = 'true' if proxy else 'false'
        if proxyStr not in self.scrapeMetrics.scrapesByProxyUsage:
            self.scrapeMetrics.scrapesByProxyUsage[proxyStr] = EventMetric()
        self.scrapeMetrics.scrapesByProxyUsage[proxyStr].addFailure()
        
        if self.currentScrapingLocName not in self.scrapeMetrics.scrapesByLocation:
            self.scrapeMetrics.scrapesByLocation[self.currentScrapingLocName] = EventMetric()
        self.scrapeMetrics.scrapesByLocation[self.currentScrapingLocName].addFailure()

        self.scrapeMetrics.totalFailures += 1
        if type not in self.scrapeMetrics.failuresByType:
            self.scrapeMetrics.failuresByType[type] = 0
        self.scrapeMetrics.failuresByType[type] += 1

    def logSuspectParse(self, domain: str):
        if domain not in self.scrapeMetrics.suspectParsesByDomain:
            self.scrapeMetrics.suspectParsesByDomain[domain] = 0
        self.scrapeMetrics.suspectParsesByDomain[domain] += 1

    def logFubarEvent(self, descriptor: str):
        self.scrapeMetrics.fubarEvents.append(descriptor)

    def pushMetrics(self):
        self.dbInterface.logScrapeMetrics(self.scrapeMetrics)