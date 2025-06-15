import sqlite3
from datetime import datetime, timedelta

class SQLiteHandler:
    def __init__(self, db_path='logs.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.init_db()

    def init_db(self):
        with self.conn:
            # Tables principales
            self.conn.executescript('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    application TEXT,
                    tag TEXT,
                    timestamp TEXT,
                    level TEXT,
                    message TEXT,
                    user TEXT,
                    module TEXT,
                    host TEXT,
                    response_time INTEGER DEFAULT 0
                );
                
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT NOT NULL,
                    application TEXT,
                    module TEXT,
                    host TEXT,
                    message TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TEXT
                );
                
                CREATE TABLE IF NOT EXISTS alert_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_threshold INTEGER DEFAULT 5,
                    warning_threshold INTEGER DEFAULT 20,
                    notification_email TEXT,
                    last_updated TEXT DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS bam_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    avg_response_time REAL,
                    success_rate REAL,
                    error_rate REAL,
                    volume INTEGER,
                    last_updated TEXT DEFAULT CURRENT_TIMESTAMP
                );
                
                INSERT OR IGNORE INTO alert_config 
                (error_threshold, warning_threshold) 
                VALUES (5, 20);
            ''')
    
    # Méthodes pour les logs
    def insert_log(self, application, tag, timestamp, level, message, 
                 user, module, host, response_time=0):
        with self.conn:
            self.conn.execute('''
                INSERT INTO logs VALUES (
                    NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            ''', (application, tag, timestamp, level, message, 
                 user, module, host, response_time))
            self._check_alert_thresholds(application, module, host, level)

    def get_logs(self, tag='', level='', application='', 
               module='', host='', limit=100):
        query = 'SELECT * FROM logs WHERE 1=1'
        params = []
        
        conditions = {
            'tag': tag,
            'level': level,
            'application': application,
            'module': module,
            'host': host
        }
        
        for field, value in conditions.items():
            if value:
                query += f' AND {field} = ?'
                params.append(value)
        
        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)
        
        return self.conn.execute(query, params).fetchall()

    def get_distinct_values(self, column):
        if column not in ['application', 'tag', 'level', 'module', 'host']:
            return []
        return [row[0] for row in 
               self.conn.execute(f'SELECT DISTINCT {column} FROM logs WHERE {column} IS NOT NULL')]

    # Méthodes pour les alertes
    def _check_alert_thresholds(self, application, module, host, level):
        config = self.get_alert_config()
        error_count = self.conn.execute('''
            SELECT COUNT(*) FROM logs 
            WHERE application = ? AND level = 'ERROR' 
            AND timestamp >= datetime('now', '-1 hour')
        ''', (application,)).fetchone()[0]
        
        if error_count >= config['error_threshold']:
            self.create_alert('CRITICAL', application, module, host, 
                            f"{error_count} errors in last hour (threshold: {config['error_threshold']})")
        elif error_count >= config['warning_threshold']:
            self.create_alert('WARNING', application, module, host,
                            f"{error_count} errors in last hour (threshold: {config['warning_threshold']})")

    def create_alert(self, level, application, module, host, message):
        with self.conn:
            self.conn.execute('''
                INSERT INTO alerts (level, application, module, host, message)
                VALUES (?, ?, ?, ?, ?)
            ''', (level, application, module, host, message))

    def get_active_alerts(self):
        return self.conn.execute('''
            SELECT * FROM alerts 
            WHERE status = 'active' 
            ORDER BY created_at DESC
        ''').fetchall()

    def get_alert_history(self, limit=50):
        return self.conn.execute('''
            SELECT * FROM alerts 
            WHERE status != 'active' 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,)).fetchall()

    def get_alert_config(self):
        return dict(self.conn.execute('SELECT * FROM alert_config LIMIT 1').fetchone())

    def update_alert_config(self, error_threshold, warning_threshold, notification_email):
        with self.conn:
            self.conn.execute('''
                UPDATE alert_config SET
                    error_threshold = ?,
                    warning_threshold = ?,
                    notification_email = ?,
                    last_updated = CURRENT_TIMESTAMP
            ''', (error_threshold, warning_threshold, notification_email))

    # Méthodes pour les statistiques
    def get_stats_summary(self, time_range='24h', application=''):
        time_condition = self._get_time_condition(time_range)
        app_condition = "AND application = ?" if application else ""
        
        query = f"""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN level = 'ERROR' THEN 1 ELSE 0 END) as errors,
                SUM(CASE WHEN level = 'WARNING' THEN 1 ELSE 0 END) as warnings,
                COUNT(DISTINCT application) as applications
            FROM logs 
            WHERE 1=1 {time_condition} {app_condition}
        """
        params = [application] if application else []
        return self.conn.execute(query, params).fetchone()

  
        
    def get_logs_by_level(self, time_range='24h', application=''):
        time_condition = self._get_time_condition(time_range)
        app_condition = "AND application = ?" if application else ""
        
        query = f"""
            SELECT 
                level, 
                COUNT(*) as count
            FROM logs 
            WHERE 1=1 {time_condition} {app_condition}
            GROUP BY level
        """
        params = [application] if application else []
        return self.conn.execute(query, params).fetchall()
        
    def get_top_applications(self, limit=5, time_range='24h', application=''):
        time_condition = self._get_time_condition(time_range)
        app_condition = "AND application = ?" if application else ""
        
        query = f"""
            SELECT 
                application, 
                COUNT(*) as count
            FROM logs 
            WHERE 1=1 {time_condition} {app_condition}
            GROUP BY application 
            ORDER BY count DESC 
            LIMIT ?
        """
        params = ([application] if application else []) + [limit]
        return self.conn.execute(query, params).fetchall()

    def _get_time_condition(self, time_range):
        if time_range == '24h': return "AND timestamp >= datetime('now', '-1 day')"
        elif time_range == '7d': return "AND timestamp >= datetime('now', '-7 days')"
        elif time_range == '30d': return "AND timestamp >= datetime('now', '-30 days')"
        return ""

    # Méthodes pour le BAM
    def _get_performance(self):
        """Calcule les métriques de performance avec gestion des valeurs nulles"""
        perf = self.conn.execute('''
            SELECT 
                AVG(response_time) as avg,
                MAX(response_time) as max,
                MIN(response_time) as min
            FROM logs 
            WHERE response_time > 0
        ''').fetchone()
        
        avg = perf['avg'] if perf and perf['avg'] is not None else 0
        return {
            'value': round(avg),
            'target': 500,
            'max': perf['max'] if perf else 0,
            'min': perf['min'] if perf else 0
        }

    def get_bam_metrics(self):
        """Récupère toutes les métriques BAM avec gestion des erreurs"""
        try:
            return {
                'metrics': {
                    'availability': self._get_availability(),
                    'performance': self._get_performance(),
                    'error_rate': self._get_error_rate()
                },
                'performance_trend': self._get_performance_trend(),
                'availability_by_app': self._get_availability_by_app(),
                'transactions': self.get_key_transactions()
            }
        except Exception as e:
            print(f"Error generating BAM metrics: {e}")
            return {
                'metrics': {
                    'availability': {'value': 0, 'target': 99.9, 'status': 'error'},
                    'performance': {'value': 0, 'target': 500, 'status': 'error'},
                    'error_rate': {'value': 0, 'target': 1, 'status': 'error'}
                },
                'performance_trend': {'labels': [], 'data': []},
                'availability_by_app': {'labels': [], 'data': []},
                'transactions': []
            }

    def _get_availability(self):
        avail = self.conn.execute('''
            SELECT (SUM(CASE WHEN level != 'ERROR' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as rate
            FROM logs
        ''').fetchone()[0] or 100
        return {'value': round(avail, 2), 'target': 99.9}


    def _get_error_rate(self):
        rate = self.conn.execute('''
            SELECT (SUM(CASE WHEN level = 'ERROR' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as rate
            FROM logs
        ''').fetchone()[0] or 0
        return {'value': round(rate, 2), 'target': 1}

    def _get_performance_trend(self):
        return {
            'labels': ['J-7', 'J-6', 'J-5', 'J-4', 'J-3', 'J-2', 'J-1'],
            'data': [350, 400, 420, 380, 410, 390, 370]  # Exemple
        }

    def _get_availability_by_app(self):
        apps = self.get_distinct_values('application')[:5]
        return {
            'labels': apps,
            'data': [99.8, 99.5, 98.9, 99.2, 99.7][:len(apps)]  # Exemple
        }

    def get_key_transactions(self):
        return self.conn.execute('''
            SELECT name, avg_response_time, success_rate, volume
            FROM bam_transactions
            ORDER BY volume DESC
        ''').fetchall()

    def update_transaction(self, name, response_time, is_success):
        with self.conn:
            self.conn.execute('''
                INSERT INTO bam_transactions VALUES (
                    NULL, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP
                ) ON CONFLICT(name) DO UPDATE SET
                    avg_response_time = ((avg_response_time * volume) + ?) / (volume + 1),
                    success_rate = ((success_rate * volume) + ?) / (volume + 1),
                    error_rate = ((error_rate * volume) + ?) / (volume + 1),
                    volume = volume + 1,
                    last_updated = CURRENT_TIMESTAMP
            ''', (
                name, response_time, 
                100 if is_success else 0, 
                0 if is_success else 100,
                response_time,
                100 if is_success else 0,
                0 if is_success else 100
            ))

    def close(self):
        if self.conn:
            self.conn.close()