import mysql.connector
from mysql.connector import errorcode

class MySQLHandler:
    def __init__(self, host='localhost', user='root', password='', database='log_db'):
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
            'raise_on_warnings': True
        }
        self.conn = None

    def init_db(self):
        try:
            self.conn = mysql.connector.connect(**self.config)
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    tag VARCHAR(255),
                    timestamp DATETIME,
                    level VARCHAR(50),
                    message TEXT
                )
            ''')
            self.conn.commit()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Erreur: Mauvais nom d'utilisateur ou mot de passe")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Erreur: Base de données inexistante")
            else:
                print(err)

    def insert_log(self, tag, timestamp, level, message):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO logs (tag, timestamp, level, message) VALUES (%s, %s, %s, %s)',
            (tag, timestamp, level, message)
        )
        self.conn.commit()

    def get_logs(self, tag='', level=''):
        cursor = self.conn.cursor()
        query = 'SELECT tag, timestamp, level, message FROM logs WHERE 1=1'
        params = []
        if tag:
            query += ' AND tag = %s'
            params.append(tag)
        if level:
            query += ' AND level = %s'
            params.append(level)
        query += ' ORDER BY timestamp DESC LIMIT 100'
        cursor.execute(query, params)
        rows = cursor.fetchall()
        logs = []
        for row in rows:
            logs.append({
                'tag': row[0],
                'timestamp': row[1].strftime('%Y-%m-%d %H:%M:%S') if row[1] else '',
                'level': row[2],
                'message': row[3]
            })
        return logs

