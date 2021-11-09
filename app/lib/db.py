import os
from pymongo import MongoClient

class Database:

  def __init__(self):
    self.db = self._connect()
    self.Links = self.db['links']
    self.Targets = self.db['targets']

  def _connect(self):
    CONNECTION_STRING = os.getenv('MONGO_URI')
    client = MongoClient(CONNECTION_STRING)
    return client['oswas-db']
  
  def createTarget(self, target):
    data = self.Targets.insert(target)
    return data 

  def createLink(self, link):
    data = self.Links.insert(link)
    return data

  def createLinksMulti(self, links):
    data = self.Links.insert_many(links)
    return data

  def updateTarget(self, targetId, updateData):
    data = self.Targets.update(
      { '_id': targetId },
      {
        '$set': updateData,
      }
    )
    return data