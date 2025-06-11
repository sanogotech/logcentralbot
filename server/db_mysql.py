import mysql.connector

class MySQLHandler:
    def __init__(self, host='localhost', user='root', password='root', database='logdb'):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.conn.autocommit = True

    def init_db(self):
        with self.conn.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    application VARCHAR(255),
                    tag VARCHAR(255),
                    timestamp DATETIME,
                    level VARCHAR(50),
                    message TEXT,
                    user VARCHAR(255),
                    module VARCHAR(255),
                    host VARCHAR(255)
                )
            ''')

    def insert_log(self, application, tag, timestamp, level, message, user, module, host):
        with self.conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO logs (application, tag, timestamp, level, message, user, module, host)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (application, tag, timestamp, level, message, user, module, host))

    def get_logs(self, tag='', level='', application=''):
        query = 'SELECT * FROM logs WHERE 1=1'
        params = []
        if tag:
            query += ' AND tag = %s'
            params.append(tag)
        if level:
            query += ' AND level = %s'
            params.append(level)
        if application:
            query += ' AND application = %s'
            params.append(application)

        query += ' ORDER BY timestamp DESC LIMIT 100'
        with self.conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, tuple(params))
            return cursor.fetchall()
