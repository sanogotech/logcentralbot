import sqlite3
import os

class SQLiteHandler:
    def __init__(self, db_path='logs.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.init_db()

    def init_db(self):
        with self.conn:
            # Création de la table avec toutes les colonnes nécessaires
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
            
            # Vérification et ajout des colonnes manquantes si nécessaire
            self._add_missing_columns()

    def _add_missing_columns(self):
        """Ajoute les colonnes manquantes à la table existante."""
        columns_to_add = {
            'module': 'TEXT',
            'host': 'TEXT'
        }
        
        cursor = self.conn.cursor()
        
        # Récupère les colonnes existantes
        cursor.execute("PRAGMA table_info(logs)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        # Ajoute les colonnes manquantes
        for column, col_type in columns_to_add.items():
            if column not in existing_columns:
                try:
                    self.conn.execute(f'ALTER TABLE logs ADD COLUMN {column} {col_type}')
                except sqlite3.OperationalError as e:
                    print(f"Impossible d'ajouter la colonne {column}: {e}")

    def insert_log(self, application, tag, timestamp, level, message, user, module, host):
        """Insère un nouveau log dans la base de données."""
        with self.conn:
            self.conn.execute('''
                INSERT INTO logs (
                    application, tag, timestamp, level, 
                    message, user, module, host
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (application, tag, timestamp, level, message, user, module, host))

    def get_logs(self, tag='', level='', application='', module='', host='', limit=100):
        """Récupère les logs avec des filtres optionnels."""
        query = 'SELECT * FROM logs WHERE 1=1'
        params = []
        
        # Construction dynamique de la requête en fonction des filtres
        if tag:
            query += ' AND tag = ?'
            params.append(tag)
        if level:
            query += ' AND level = ?'
            params.append(level)
        if application:
            query += ' AND application = ?'
            params.append(application)
        if module:
            query += ' AND module = ?'
            params.append(module)
        if host:
            query += ' AND host = ?'
            params.append(host)

        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)
        
        cur = self.conn.cursor()
        cur.execute(query, params)
        return cur.fetchall()

    def get_distinct_values(self, column):
        """Récupère les valeurs distinctes pour une colonne donnée."""
        if column not in ['application', 'tag', 'level', 'module', 'host']:
            return []
            
        query = f'SELECT DISTINCT {column} FROM logs WHERE {column} IS NOT NULL ORDER BY {column}'
        cur = self.conn.cursor()
        cur.execute(query)
        return [row[0] for row in cur.fetchall()]

    def close(self):
        """Ferme la connexion à la base de données."""
        if self.conn:
            self.conn.close()