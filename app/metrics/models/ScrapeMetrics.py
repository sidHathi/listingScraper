from pydantic import BaseModel
from datetime import datetime

from .EventMetric import EventMetric

class ScrapeMetrics(BaseModel):
    timestamp: datetime
    allScrapes: EventMetric
    scrapesByDomain: dict[str, EventMetric]
    scrapesByProxyUsage: dict[str, EventMetric]
    scrapesByLocation: dict[str, EventMetric]
    suspectParsesByDomain: dict[str, int]
    totalFailures: int
    failuresByType: dict[str, int]
    fubarEvents: list[str]
