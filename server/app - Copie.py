import argparse
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from db_factory import get_db_handler

app = Flask(__name__)
db = None

@app.context_processor
def inject_global_vars():
    return {
        'now': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'app_name': 'LogsApp'
    }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/logs')
def view_logs():
    filters = {
        'tag': request.args.get('tag', ''),
        'level': request.args.get('level', ''),
        'application': request.args.get('application', ''),
        'module': request.args.get('module', ''),
        'host': request.args.get('host', '')
    }
    
    logs = db.get_logs(
        tag=filters['tag'],
        level=filters['level'],
        application=filters['application'],
        module=filters['module'],
        host=filters['host']
    )
    
    stats = {
        'total': len(logs),
        'info': sum(1 for log in logs if log['level'] == 'INFO'),
        'warnings': sum(1 for log in logs if log['level'] == 'WARNING'),
        'errors': sum(1 for log in logs if log['level'] == 'ERROR')
    }
    
    return render_template('logs.html', logs=logs, stats=stats, **filters)

@app.route('/alerts')
def view_alerts():
    active_alerts = db.get_active_alerts()
    alert_history = db.get_alert_history(limit=50)
    alert_config = db.get_alert_config()
    
    return render_template(
        'alerts.html',
        active_alerts=active_alerts,
        alert_history=alert_history,
        alert_config=alert_config
    )


@app.route('/stats')
def view_stats():
    time_range = request.args.get('time_range', '24h')
    application = request.args.get('application', '')
    
    # Récupération des données
    stats = db.get_stats_summary(time_range, application)
    level_data = db.get_logs_by_level(time_range, application)
    top_apps = db.get_top_applications(5, time_range, application)
    
    # Préparation des données pour les graphiques
    level_labels = [row['level'] for row in level_data]
    level_counts = [row['count'] for row in level_data]
    
    app_labels = [app['application'] for app in top_apps]
    app_counts = [app['count'] for app in top_apps]
    
    return render_template(
        'stats.html',
        stats=stats,
        level_labels=level_labels,
        level_counts=level_counts,
        app_labels=app_labels,
        app_counts=app_counts,
        applications=db.get_distinct_values('application'),
        current_time_range=time_range,
        current_application=application
    )

@app.route('/bam')
def view_bam():
    bam_data = db.get_bam_metrics()
    return render_template('bam.html', **bam_data)

@app.route('/receive_logs', methods=['POST'])
@app.route('/api/logs', methods=['POST'])
def receive_logs():
    data = request.get_json()
    
    if not data or not isinstance(data.get('logs'), list):
        return jsonify({'error': 'Invalid data format'}), 400
    
    inserted_count = 0
    errors = []
    
    for log in data['logs']:
        try:
            db.insert_log(
                application=log.get('application', 'Unknown'),
                tag=log.get('tag', 'general'),
                timestamp=log.get('timestamp', datetime.now().isoformat()),
                level=log.get('level', 'INFO').upper(),
                message=log.get('message', ''),
                user=log.get('user', 'system'),
                module=log.get('module', 'main'),
                host=log.get('host', 'localhost'),
                response_time=log.get('response_time', 0)
            )
            inserted_count += 1
        except Exception as e:
            errors.append(str(e))
    
    return jsonify({
        'message': f'Inserted {inserted_count}/{len(data["logs"])} logs',
        'inserted': inserted_count,
        'errors': errors
    }), 200 if inserted_count > 0 else 400

def initialize_db(db_type='sqlite'):
    global db
    db = get_db_handler(db_type)
    db.init_db()
    print(f"Database initialized ({db_type})")

def main():
    parser = argparse.ArgumentParser(description='LogsApp Server')
    parser.add_argument('--dbtype', choices=['sqlite', 'mysql', 'mongodb'], 
                      default='sqlite', help='Database type')
    parser.add_argument('--host', default='0.0.0.0', help='Server host')
    parser.add_argument('--port', type=int, default=5000, help='Server port')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    
    args = parser.parse_args()
    initialize_db(args.dbtype)
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == '__main__':
    main()