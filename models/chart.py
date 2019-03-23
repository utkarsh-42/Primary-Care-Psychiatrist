import uuid
import datetime
from common.database import Database


class Chart(object):
    def __init__(self, name, author, description, author_id, _id=None):
        self.name = name
        self.author = author
        self.author_id = author_id
        self.description = description
        self._id = uuid.uuid4().hex if _id is None else _id

    def save_to_mongo(self):
        Database.insert(collection="analyze",
                        data=self.json())

    def json(self):
        return {
            'name' : self.name,
            'author': self.author,
            'author_id': self.author_id,
            'description': self.description,
            '_id': self._id
        }

    @classmethod
    def from_mongo(cls, id):
        analyze_data = Database.find_one(collection='analyze',
                                      query={'_id': id})
        return cls(**analyze_data)

    @classmethod
    def find_by_author_id(cls, author_id):
        analyze = Database.find(collection='analyze',
                              query={'author_id': author_id})
        return analyze
