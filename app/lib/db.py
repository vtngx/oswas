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
    self.Targets.insert(target)

  def createLink(self, link):
    self.Links.insert(link)

  def createLinksMulti(self, links):
    self.Links.insert_many(links)

  def updateTarget(self, targetId, updateData):
    self.Targets.update(
      { '_id': targetId },
      {
        '$set': updateData,
      }
    ) 