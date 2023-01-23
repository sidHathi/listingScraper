import sys
import asyncio
from typing import TextIO

from ..utils.requestUtils import buildBlacklist
from ..loggers.RequestLogger import RequestLogger
from ..loggers.ScrapeLogger import ScrapeLogger
from ..DBInterface import DBInterface
from ..RequestHub import RequestHub
from .App import App
from ..metrics.MetricsController import MetricsController


async def main() -> None:
    blacklist: dict[str, set[str]] | None = buildBlacklist()
    scrapeLogFile: TextIO = open('scrapeLog.log', 'w+')
    requestLogFile: TextIO = open('requestLog.log', 'w+')
    blacklistLogFile: TextIO = open('blacklist.log', 'w+')

    dbInterface: DBInterface = DBInterface()
    metricsController: MetricsController = MetricsController(dbInterface)
    requestLogger: RequestLogger = RequestLogger(requestLogFile, metricsController)
    scrapeLogger: ScrapeLogger = ScrapeLogger(scrapeLogFile, metricsController)
    requestHub: RequestHub = RequestHub(requestLogger)
    if blacklist is not None:
        requestLogger.addBlacklist(blacklist, blacklistLogFile)
        requestHub.addBlacklist(blacklist)
    app: App = App(dbInterface, requestHub, scrapeLogger)

    await app.run()
    requestLogger.dumpLogs()
    scrapeLogFile.close()
    requestLogFile.close()
    metricsController.pushMetrics()
    blacklistLogFile.close()
    

if (__name__ == '__main__'):
    sys.exit(asyncio.run(main()))