from typing import Dict
from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()
class Database:

  def __init__(self) -> None:
      self.client = MongoClient(f"mongodb+srv://{os.environ['DB_USERNAME']}:{os.environ['DB_PASSWORD']}@cluster0.mskkl.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

  def update(self, queryObj: Dict, updateObj: Dict):
    collection = self.client['feedback']['record']
    result = collection.update_one(queryObj, { "$set" : updateObj })
    return result
  