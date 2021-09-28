import os

from pymongo import MongoClient

class Database:

  def __init__(self):
    self._connect()

  def _connect(self):
    CONNECTION_STRING = os.getenv("MONGO_URI")
    print(CONNECTION_STRING)
    client = MongoClient(CONNECTION_STRING)
    return client["oswas-db"]
  
  