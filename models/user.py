import datetime
import uuid
from flask import session
from models.chart import Chart
from common.database import Database

class User(object):
    def __init__(self, name, email, password, _id=None):
        self.name = name
        self.email = email
        self.password = password
        self._id = uuid.uuid4().hex if _id is None else _id

    @classmethod
    def get_by_email(cls, email):
        data = Database.find_one("users", {"email": email})
        if data is not None:
            return cls(**data)

    @classmethod
    def get_by_id(cls, _id):
        data = Database.find_one("users", {"_id": _id})
        if data is not None:
            return cls(**data)

    @staticmethod
    def login_valid(email, password):
        user = User.get_by_email(email)
        if user is not None:
            # Check the password
            return user.password == password
        return False

    @classmethod
    def register(cls, name, email, password):
        user = cls.get_by_email(email)
        if user is None:
            # User doesn't exists so we can create it
            new_user = cls(name, email, password)
            new_user.save_to_mongo()
            session['email'] = email
            return True
        else:
            return False

    @staticmethod
    def login(user_email):
        session['email'] = user_email

    @staticmethod
    def logout():
        session['email'] = None

    def get_analyze(self):
        return Chart.find_by_author_id(self._id)

    def new_analyze(self, description):
        analyze = Chart(name=self.name,
                    author=self.email,
                    description=description,
                    author_id=self._id)
        analyze.save_to_mongo()

    def json(self):
        return {
            'name' : self.name,
            'email': self.email,
            '_id': self._id,
            'password': self.password
        }

    def save_to_mongo(self):
        Database.insert("users", self.json())
