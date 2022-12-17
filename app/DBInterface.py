from pymongo import MongoClient
from dotenv import dotenv_values
from .models.Listing import Listing
from typing import Any

config = dotenv_values(".env")

class DBInterface:
    def __init__(self):
        if config["ATLAS_URI"] is None or config["DB_NAME"] is None or config['LISTINGS_COLLECTION_NAME'] is None or config['MIGRATIONS_COLLECTION_NAME'] is None or config['QUERIES_COLLECTION_NAME'] is None:
            raise Exception("env variables not configured")
        
        client = MongoClient(str(config['ATLAS_URI']))
        self.db = client[config['DB_NAME']]
        self.listingsCol = self.db[config['LISTINGS_COLLECTION_NAME']]
        self.migrationsCol = self.db[config['MIGRATIONS_COLLECTION_NAME']]
        self.queriesCol = self.db[config['QUERIES_COLLECTION_NAME']]

    def getListingUrls(self) -> list[dict[str, str]]:
        return list(self.listingsCol.find({}, {'_id': 1, 'url': 1, 'scrapeTime': 1}))

    def getListingUrlsByProvider(self) -> list[dict[str, str]]:
        return list(self.listingsCol.find({}, {'_id': 1, 'providerName': 1, 'url': 1, 'scrapeTime': 1}))

    def addListing(self, listing: Listing):
        return self.listingsCol.insert_one(listing.toJson())

    def removeListing(self, listingId: str):
        return self.listingsCol.delete_one({'_id': listingId})

    def updateListingField(self, docId: str, fieldName: str, newVal: Any):
        return self.listingsCol.update_one({'_id': docId}, {'$set': {fieldName: newVal}})

    def removeListingField(self, fieldName: str):
        return self.listingsCol.update_many({}, {'$unset': {fieldName: ""}})

    def getMigrationIndices(self) -> list[int]:
        return list(map(
            lambda col: col['index'],
            self.migrationsCol.find({}, {'_id': 0, 'index': 1})
        ))
    
    def addMigration(self, description: str, index: int, fields: list[str]):
        return self.migrationsCol.insert_one({
            'index': index,
            'description': description,
            'fields': fields
        })
    
    def removeMigration(self, index: int):
        self.migrationsCol.delete_one({'index': index})

    def getQueries(self) -> list[dict[str, Any]]:
        return list(self.queriesCol.find())

