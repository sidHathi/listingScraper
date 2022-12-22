import sys
import asyncio
from typing import cast

from ..DBInterface import DBInterface
from ..RequestHub import RequestHub
from .App import App


async def main() -> None:
    dbInterface: DBInterface = DBInterface()
    requestHub: RequestHub = RequestHub()
    app: App = App(dbInterface, requestHub)

    await app.run()
    

if (__name__ == '__main__'):
    sys.exit(asyncio.run(main()))