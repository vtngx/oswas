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
    return client['oswas']
  
  def create_target(self, target):
    data = self.Targets.insert(target)
    return data 

  def create_link(self, link):
    data = self.Links.insert(link)
    return data

  def create_links_multi(self, links):
    if len(links) != 0:
      data = self.Links.insert_many(links)
      return data

  def update_target(self, target_id, update_data):
    data = self.Targets.update(
      { '_id': target_id },
      {
        '$set': update_data,
      }
    )
    return data

  def get_output_links(self, target_id, user_type):
    links = self.Links.find({
      "target_id": target_id,
      "user": user_type,
    })
    return list(links)

  def get_all_target_links(self, target_id):
    links = self.Links.find({
      "target_id": target_id,
    })
    return list(links)
  
  def get_all_targets(self):
    targets = self.Targets.find({}).sort("started_at", -1)
    return list(targets)

  def count_target_links(self, target_id):
    links = self.Links.find({
      "target_id": target_id,
    })
    return len(list(links))