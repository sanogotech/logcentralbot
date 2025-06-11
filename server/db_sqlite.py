import sqlite3
from datetime import datetime

class SQLiteHandler:
    def __init__(self, db_file='log_db.sqlite'):
        self.db_file = db_file
        self.conn = None

    def init_db(self):
        self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag TEXT,
                timestamp TEXT,
                level TEXT,
                message TEXT
            )
        ''')
        self.conn.commit()

    def insert_log(self, tag, timestamp, level, message):
        cur = self.conn.cursor()
        cur.execute('INSERT INTO logs (tag, timestamp, level, message) VALUES (?, ?, ?, ?)',
                    (tag, timestamp, level, message))
        self.conn.commit()

    def get_logs(self, tag='', level=''):
        cur = self.conn.cursor()
        query = 'SELECT tag, timestamp, level, message FROM logs WHERE 1=1'
        params = []
        if tag:
            query += ' AND tag = ?'
            params.append(tag)
        if level:
            query += ' AND level = ?'
            params.append(level)
        query += ' ORDER BY timestamp DESC LIMIT 100'
        cur.execute(query, params)
        rows = cur.fetchall()
        logs = []
        for row in rows:
            logs.append({
                'tag': row[0],
                'timestamp': row[1],
                'level': row[2],
                'message': row[3]
            })
        return logs

