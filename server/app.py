import argparse
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from db_factory import get_db_handler

from flask import jsonify
import logging

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
        'host': request.args.get('host', ''),
        'response_time': request.args.get('response_time', '')
    }
    
    logs = db.get_logs(
        tag=filters['tag'],
        level=filters['level'],
        application=filters['application'],
        module=filters['module'],
        host=filters['host'],
        response_time=filters['response_time']
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
    applications = db.get_distinct_values('application')  # Nouveau
    
    return render_template(
        'alerts.html',
        active_alerts=active_alerts,
        alert_history=alert_history,
        alert_config=alert_config,
        applications=applications
    )


@app.route('/api/alerts/config', methods=['POST'])
def update_alert_config():
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 415
    
    data = request.get_json()
    try:
        db.update_alert_config(
            error_threshold=int(data.get('error_threshold')),
            warning_threshold=int(data.get('warning_threshold')),
            notification_email=data.get('notification_email'),
            monitored_application=data.get('monitored_application')
        )
        
        # Nouveau : Recalculer les alertes après modification
        db.recheck_all_alerts()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/alerts/test-email', methods=['POST'])
def test_email():
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 415
    
    data = request.get_json()
    email = data.get('email')
    application = data.get('application')
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    try:
        # Ajoutez des logs pour débogage
        app.logger.info(f"Tentative d'envoi d'email test à {email}")
        success = db.send_test_email(email, application)
        if success:
            app.logger.info("Email test envoyé avec succès")
            return jsonify({'status': 'success', 'message': 'Email test sent'})
        else:
            app.logger.error("Échec de l'envoi de l'email test")
            return jsonify({'error': 'Failed to send test email'}), 500
    except Exception as e:
        app.logger.error(f"Erreur lors de l'envoi d'email test: {str(e)}")
        return jsonify({'error': str(e)}), 500
        


@app.route('/api/alerts/<int:alert_id>/resolve', methods=['POST'])
def resolve_alert(alert_id):
    db.resolve_alert(alert_id)
    return jsonify({'status': 'success'})



@app.route('/api/alerts/active', methods=['GET'])
def get_active_alerts():
    try:
        active_alerts = db.get_active_alerts()
        
        # À ajouter temporairement dans votre code
        print("Test get_active_alerts:")
        print(f"Nombre d'alertes actives: {len(active_alerts)}")
        for alert in active_alerts:
            print(dict(alert))  # Conversion en dict pour une meilleure lisibilité
        
        # Retournez directement le tableau sans wrapper dans un objet
        if not active_alerts:
            return jsonify([])  # Retourne un tableau vide directement
            
        # Convertir les Row objects en dicts
        alerts_data = [dict(alert) for alert in active_alerts]
        return jsonify(alerts_data)  # Retourne le tableau directement
        
    except Exception as e:
        app.logger.error(f"Erreur : {str(e)}")
        return jsonify([]), 500  # Retourne un tableau vide même en cas d'erreur



# @app.route('/api/alerts/active', methods=['GET'])
# def get_active_alerts():
    # # Données factices (à supprimer après test)
    # test_data = [{
        # "id": 999,
        # "level": "critical",
        # "application": "TestApp",
        # "message": "Ceci est une alerte de test",
        # "created_at": datetime.utcnow().isoformat()
    # }]
    
    # return jsonify(test_data)  # Si ça s'affiche, le problème vient de la requête DB

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