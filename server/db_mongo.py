from pymongo import MongoClient
from datetime import datetime

class MongoDBHandler:
    def __init__(self, uri='mongodb://localhost:27017', db_name='logdb'):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db['logs']

    def init_db(self):
        # MongoDB is schema-less, but we can create an index for performance
        self.collection.create_index([("timestamp", -1)])

    def insert_log(self, application, tag, timestamp, level, message, user, module, host):
        self.collection.insert_one({
            'application': application,
            'tag': tag,
            'timestamp': datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'),
            'level': level,
            'message': message,
            'user': user,
            'module': module,
            'host': host
        })

    def get_logs(self, tag='', level='', application=''):
        query = {}
        if tag:
            query['tag'] = tag
        if level:
            query['level'] = level
        if application:
            query['application'] = application

        cursor = self.collection.find(query).sort('timestamp', -1).limit(100)
        return list(cursor)
