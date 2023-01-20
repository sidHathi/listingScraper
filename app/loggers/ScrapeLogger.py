from typing import TextIO, Any
from urllib.parse import urlparse

from ..enums import ListingField
from ..utils.ListingFlagger import ListingFlagger
from ..metrics.MetricsController import MetricsController

class ScrapeLogger:
    def __init__(self, file: TextIO | None = None, metricsController: MetricsController | None = None):
        self.store: dict[str, dict[ListingField, str | None]] = {}
        self.logFile: TextIO | None = file
        self.listingFlagger: ListingFlagger = ListingFlagger()
        self.metricsController = metricsController

    def addEvent(self, url: str, field: ListingField, parsedData: str | None):
        if url not in self.store:
            self.store[url] = {}

        self.store[url][field] = parsedData

    def isPriceValid(self, price: int) -> bool:
        return self.listingFlagger.checkValidPrice(price)
    
    def isBedroomsValid(self, bedrooms: list[int]) -> bool:
        return self.listingFlagger.checkValidBedrooms(bedrooms)
    
    def isShortestLeaseValid(self, val: int) -> bool:
        return self.listingFlagger.checkValidLeaseTerm(val)

    def checkVal(self, url: str, field: ListingField, parsedData: Any):
        domain: str = urlparse(url).netloc
        match field:
            case ListingField.Price:
                if not self.isPriceValid(parsedData):
                    self.addEvent(url, field, parsedData)
                    if self.metricsController is not None:
                        self.metricsController.logSuspectParse(domain)
                    return
            case ListingField.Bedrooms:
                if not self.isBedroomsValid(parsedData):
                    self.addEvent(url, field, parsedData)
                    if self.metricsController is not None:
                        self.metricsController.logSuspectParse(domain)
                    return
            case ListingField.ShortestLease:
                if not self.isShortestLeaseValid(parsedData):
                    self.addEvent(url, field, parsedData)
                    if self.metricsController is not None:
                        self.metricsController.logSuspectParse(domain)
                    return
            case _:
                return

    def formatStore(self) -> str:
        return str(self.store)

    def dumpLogs(self):
        if self.logFile is None:
            print(self.formatStore());
            return
        
        self.logFile.write(self.formatStore())