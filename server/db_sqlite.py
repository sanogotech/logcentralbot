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
                    resolved_at TEXT,
                    email_sent BOOLEAN DEFAULT FALSE
                );
                
                CREATE TABLE IF NOT EXISTS alert_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_threshold INTEGER DEFAULT 5,
                    warning_threshold INTEGER DEFAULT 20,
                    notification_email TEXT,
                    monitored_application TEXT,
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
           module='', host='', response_time='', limit=100):
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
            
            if response_time:
                if response_time == 'fast':
                    query += ' AND response_time < 100'
                elif response_time == 'medium':
                    query += ' AND response_time >= 100 AND response_time < 500'
                elif response_time == 'slow':
                    query += ' AND response_time >= 500'
            
            query += ' ORDER BY timestamp DESC LIMIT ?'
            params.append(limit)
            
            return self.conn.execute(query, params).fetchall()

    def get_distinct_values(self, column):
        if column not in ['application', 'tag', 'level', 'module', 'host']:
            return []
        return [row[0] for row in 
               self.conn.execute(f'SELECT DISTINCT {column} FROM logs WHERE {column} IS NOT NULL')]

    # Méthodes pour les alertes
    
    def recheck_all_alerts(self):
        """Recheck tous les logs récents après changement de configuration"""
        config = self.get_alert_config()
        apps = self.get_distinct_values('application')
        
        for app in apps:
            if config['monitored_application'] and config['monitored_application'] != app:
                continue
                
            # Vérifie les erreurs pour chaque application
            self._check_alert_thresholds(app, None, None, 'ERROR')
        
    def _check_alert_thresholds(self, application, module, host, level):
        config = self.get_alert_config()
        
        # Vérifier si l'application est surveillée
        if config['monitored_application'] and config['monitored_application'] != application:
            return
        
        error_count = self.conn.execute('''
            SELECT COUNT(*) FROM logs 
            WHERE application = ? AND level = 'ERROR' 
            AND timestamp >= datetime('now', '-1 hour')
        ''', (application,)).fetchone()[0]
        
        if error_count >= config['error_threshold']:
            alert_msg = f"{error_count} errors in last hour (threshold: {config['error_threshold']})"
            self.create_alert('CRITICAL', application, module, host, alert_msg)
            self._send_email_notification(config.get('notification_email'), "CRITICAL Alert", alert_msg)
        elif error_count >= config['warning_threshold']:
            alert_msg = f"{error_count} errors in last hour (threshold: {config['warning_threshold']})"
            self.create_alert('WARNING', application, module, host, alert_msg)
            self._send_email_notification(config.get('notification_email'), "WARNING Alert", alert_msg)

    def _send_email_notification(self, email, subject, message):
        if not email:
            return
            
        log_entry = f"{datetime.now().isoformat()} - Alerte envoyée à {email}\n"
        log_entry += f"Sujet: {subject}\nMessage: {message}\n\n"
        
        with open('sendEmail.log', 'a') as f:
            f.write(log_entry)
        
        # Code commenté pour l'envoi réel...

    def create_alert(self, level, application, module, host, message):
        with self.conn:
            self.conn.execute('''
                INSERT INTO alerts (level, application, module, host, message, email_sent)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (level, application, module, host, message, False))

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
        """Récupère la configuration des alertes"""
        row = self.conn.execute('SELECT * FROM alert_config LIMIT 1').fetchone()
        if row:
            return dict(row)
        return {
            'error_threshold': 5,
            'warning_threshold': 20,
            'notification_email': None,
            'monitored_application': None,
            'last_updated': datetime.now().isoformat()
        }
                
    def update_alert_config(self, error_threshold, warning_threshold, notification_email, monitored_application=None):
        with self.conn:
            self.conn.execute('''
                UPDATE alert_config SET
                    error_threshold = ?,
                    warning_threshold = ?,
                    notification_email = ?,
                    monitored_application = ?,
                    last_updated = CURRENT_TIMESTAMP
            ''', (error_threshold, warning_threshold, notification_email, monitored_application))

    def resolve_alert(self, alert_id):
        with self.conn:
            self.conn.execute('''
                UPDATE alerts SET
                    status = 'resolved',
                    resolved_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (alert_id,))

    def send_test_email(self, email, application=None):
        subject = f"Test d'alerte pour {application}" if application else "Test d'alerte"
        message = f"Ceci est un email test pour {application}" if application else "Ceci est un email test"
        
        log_entry = f"{datetime.now().isoformat()} - Email test à {email}\n"
        log_entry += f"Sujet: {subject}\nMessage: {message}\n\n"
        
        with open('sendEmail.log', 'a') as f:
            f.write(log_entry)
            return True
        
        # Code commenté pour l'envoi réel:
        '''
        import smtplib
        from email.mime.text import MIMEText
        
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = 'alerts@logsapp.com'
        msg['To'] = email
        
        with smtplib.SMTP('smtp.example.com', 587) as server:
            server.starttls()
            server.login('user', 'password')
            server.send_message(msg)
        '''

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