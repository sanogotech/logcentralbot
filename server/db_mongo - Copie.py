from pymongo import MongoClient
from datetime import datetime

class MongoHandler:
    def __init__(self, uri='mongodb://localhost:27017/', dbname='log_db'):
        self.client = MongoClient(uri)
        self.db = self.client[dbname]
        self.collection = self.db.logs

    def init_db(self):
        # Index pour accélérer les recherches
        self.collection.create_index([('tag', 1)])
        self.collection.create_index([('level', 1)])
        self.collection.create_index([('timestamp', -1)])

    def insert_log(self, tag, timestamp, level, message):
        doc = {
            'tag': tag,
            'timestamp': datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'),
            'level': level,
            'message': message
        }
        self.collection.insert_one(doc)

    def get_logs(self, tag='', level=''):
        query = {}
        if tag:
            query['tag'] = tag
        if level:
            query['level'] = level
        cursor = self.collection.find(query).sort('timestamp', -1).limit(100)
        logs = []
        for doc in cursor:
            logs.append({
                'tag': doc['tag'],
                'timestamp': doc['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                'level': doc['level'],
                'message': doc['message']
            })
        return logs

