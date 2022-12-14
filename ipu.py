import datetime
import uuid

from pymongo import MongoClient
from dotenv import dotenv_values

config = dotenv_values(".env")

def addSampleDatum():
    if config["ATLAS_URI"] is None or config["DB_NAME"] is None:
        raise Exception("env variables not configured")

    print(config["ATLAS_URI"])
    client = MongoClient(str(config["ATLAS_URI"]))
    db = client[config["DB_NAME"]]

    randUuid = uuid.uuid1()
    currentDateTime = datetime.datetime.now()
    newDataPoint = {"uuid": str(randUuid), "datetime" : currentDateTime}

    db["pyTestData"].insert_one(newDataPoint)

addSampleDatum()

