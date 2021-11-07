from typing import Dict
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId

load_dotenv()


class Database:
    def __init__(self) -> None:
        self.client = MongoClient(
            f"mongodb+srv://{os.environ['DB_USERNAME']}:{os.environ['DB_PASSWORD']}@cluster0.mskkl.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
        )

    def update(self, queryObj: Dict, updateObj: Dict):
        collection = self.client["feedback"]["record"]
        result = collection.update_one(queryObj, {"$set": updateObj})
        return result

    def find(self, queryObj: Dict, projectionObj={}):
        collection = self.client[os.environ["DB_NAME"]]["records"]
        result = [doc for doc in collection.find(queryObj, projectionObj)]
        return result

    def findUserById(self, userId: str):
        collection = self.client[os.environ["DB_NAME"]]["users"]
        result = [
            doc for doc in collection.find({"_id": ObjectId(userId)}, {"password": 0})
        ]
        return result

    def close(self):
        self.client.close()
