import sqlite3
import os

class SQLiteHandler:
    def __init__(self, db_path='logs.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def init_db(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    application TEXT,
                    tag TEXT,
                    timestamp TEXT,
                    level TEXT,
                    message TEXT,
                    user TEXT,
                    module TEXT,
                    host TEXT
                )
            ''')

    def insert_log(self, application, tag, timestamp, level, message, user, module, host):
        with self.conn:
            self.conn.execute('''
                INSERT INTO logs (application, tag, timestamp, level, message, user, module, host)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (application, tag, timestamp, level, message, user, module, host))

    def get_logs(self, tag='', level='', application=''):
        query = 'SELECT * FROM logs WHERE 1=1'
        params = []
        if tag:
            query += ' AND tag = ?'
            params.append(tag)
        if level:
            query += ' AND level = ?'
            params.append(level)
        if application:
            query += ' AND application = ?'
            params.append(application)

        query += ' ORDER BY timestamp DESC LIMIT 100'
        cur = self.conn.cursor()
        cur.execute(query, params)
        return cur.fetchall()
