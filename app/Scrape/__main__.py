import sys
import asyncio
from typing import TextIO

from ..loggers.RequestLogger import RequestLogger
from ..DBInterface import DBInterface
from ..RequestHub import RequestHub
from .App import App


async def main() -> None:
    scrapeLogFile: TextIO = open('scrapeLog.log', 'w+')
    requestLogFile: TextIO = open('requestLog.log', 'w+')

    requestLogger: RequestLogger = RequestLogger(requestLogFile)
    dbInterface: DBInterface = DBInterface()
    requestHub: RequestHub = RequestHub(requestLogger)
    app: App = App(dbInterface, requestHub, scrapeLogFile)

    await app.run()
    requestLogger.dumpLogs()
    scrapeLogFile.close()
    requestLogFile.close()
    

if (__name__ == '__main__'):
    sys.exit(asyncio.run(main()))