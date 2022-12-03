import sys
import asyncio
from geopy.geocoders import Nominatim
from geopy.location import Location
from typing import cast

from ..DBInterface import DBInterface
from .App import App


async def main() -> None:
    dbInterface: DBInterface = DBInterface()
    app: App = App(dbInterface)

    await app.run()
    

if (__name__ == '__main__'):
    sys.exit(asyncio.run(main()))