import os
from dotenv import load_dotenv
from pymongo import MongoClient

class Database:

  def __init__(self):
    load_dotenv()
    self.db = self._connect()
    self.LINKS = self.db['links']
    self.TARGETS = self.db['targets']

  def _connect(self):
    CONNECTION_STRING = os.getenv('MONGO_URI')
    client = MongoClient(CONNECTION_STRING)
    return client['oswas']
  
  def create_target(self, target):
    data = self.TARGETS.insert_one(target)
    return data.inserted_id

  def create_link(self, link):
    data = self.LINKS.insert_one(link)
    return data.inserted_id

  def create_links_multi(self, links):
    if len(links) != 0:
      data = self.LINKS.insert_many(links)
      return data

  def update_target(self, target_id, update_data):
    self.TARGETS.update_one(
      { '_id': target_id },
      {
        '$set': update_data,
      }
    )

  def get_output_links(self, target_id, user_type):
    links = self.LINKS.find({
      "target_id": target_id,
      "user": user_type,
    })
    return list(links)

  def get_all_target_links(self, target_id):
    links = self.LINKS.find({
      "target_id": target_id,
    })
    return list(links)
  
  def get_all_targets(self):
    targets = self.TARGETS.find({}).sort("started_at", -1)
    return list(targets)

  def count_target_links(self, target_id):
    links = self.LINKS.find({
      "target_id": target_id,
    })
    return len(list(links))