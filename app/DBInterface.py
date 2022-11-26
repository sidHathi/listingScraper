from pymongo import MongoClient
from dotenv import dotenv_values
from .models.Listing import Listing
from typing import Any

config = dotenv_values(".env")

class DBInterface:
    def __init__(self):
        if config["ATLAS_URI"] is None or config["DB_NAME"] is None or config['LISTINGS_COLLECTION_NAME'] is None:
            raise Exception("env variables not configured")
        
        client = MongoClient(str(config['ATLAS_URI']))
        self.db = client[config['DB_NAME']]
        self.listingsCol = self.db[config['LISTINGS_COLLECTION_NAME']]

    def getListingUrls(self) -> list[dict[str, Any]]:
        return list(self.listingsCol.find({}, {'_id': 1, 'url': 1}))

    def addListing(self, listing: Listing):
        return self.listingsCol.insert_one(listing.toJson())

    def removeListing(self, listingId: str):
        return self.listingsCol.delete_one({'_id': listingId})

    

