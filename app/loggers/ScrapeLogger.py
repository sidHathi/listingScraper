from typing import TextIO, Any

from ..enums import ListingField

class ScrapeLogger:
    def __init__(self, file: TextIO | None = None):
        self.store: dict[str, dict[ListingField, str | None]] = {}
        self.logFile: TextIO | None = file

    def addEvent(self, url: str, field: ListingField, parsedData: str | None):
        if url not in self.store:
            self.store[url] = {}

        self.store[url][field] = parsedData

    def isPriceValid(self, price: int) -> bool:
        if price < 0 or price < 500 or price > 10000:
            return False
        return True
    
    def isBedroomsValid(self, bedrooms: list[int]) -> bool:
        if len(bedrooms) < 2 or bedrooms[0] > 4 or bedrooms[1] > 4:
            return False
        return True
    
    def isShortestLeaseValid(self, val: int) -> bool:
        if val < 0 or val > 24:
            return False
        return True

    def checkVal(self, url: str, field: ListingField, parsedData: Any):
        match field:
            case ListingField.Price:
                if not self.isPriceValid(parsedData):
                    self.addEvent(url, field, parsedData)
                    return
            case ListingField.Bedrooms:
                if not self.isBedroomsValid(parsedData):
                    self.addEvent(url, field, parsedData)
                    return
            case ListingField.ShortestLease:
                if not self.isShortestLeaseValid(parsedData):
                    self.addEvent(url, field, parsedData)
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