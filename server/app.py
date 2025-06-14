import argparse
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from db_factory import get_db_handler

# Initialisation de l'application Flask
app = Flask(__name__)
db = None

@app.context_processor
def inject_global_vars():
    """Injecte des variables globales dans tous les templates"""
    return {
        'now': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'app_name': 'LogsApp'
    }

@app.route('/')
def home():
    """Route pour la page d'accueil"""
    return render_template('index.html')

@app.route('/logs')
def view_logs():
    """Route pour l'affichage des logs avec filtres"""
    # Récupération des paramètres de filtrage
    filters = {
        'tag': request.args.get('tag', ''),
        'level': request.args.get('level', ''),
        'application': request.args.get('application', ''),
        'module': request.args.get('module', ''),
        'host': request.args.get('host', '')
    }
    
    # Récupération des logs depuis la base de données
    logs = db.get_logs(
        tag=filters['tag'],
        level=filters['level'],
        application=filters['application'],
        module=filters['module'],
        host=filters['host']
    )
    
    # Préparation des données pour le template
    stats = {
        'total': len(logs),
        'info': sum(1 for log in logs if log['level'] == 'INFO'),
        'warnings': sum(1 for log in logs if log['level'] == 'WARNING'),
        'errors': sum(1 for log in logs if log['level'] == 'ERROR')
    }
    
    return render_template(
        'logs.html',
        logs=logs,
        stats=stats,
        **filters
    )

@app.route('/receive_logs', methods=['POST'])
@app.route('/api/logs', methods=['POST'])
def receive_logs():
    """Endpoint API pour recevoir les logs"""
    data = request.get_json()
    
    # Validation des données
    if not data:
        return jsonify({'error': 'No JSON data received'}), 400
        
    if not isinstance(data.get('logs'), list):
        return jsonify({'error': 'Invalid logs format'}), 400
    
    # Traitement des logs
    inserted_count = 0
    errors = []
    
    for i, log in enumerate(data['logs']):
        try:
            db.insert_log(
                application=log.get('application', 'Unknown'),
                tag=log.get('tag', 'general'),
                timestamp=log.get('timestamp', datetime.now().isoformat()),
                level=log.get('level', 'INFO').upper(),
                message=log.get('message', ''),
                user=log.get('user', 'system'),
                module=log.get('module', 'main'),
                host=log.get('host', 'localhost')
            )
            inserted_count += 1
        except Exception as e:
            errors.append(f"Log {i}: {str(e)}")
    
    # Réponse de l'API
    response = {
        'message': f'Successfully inserted {inserted_count}/{len(data["logs"])} logs',
        'inserted': inserted_count,
        'errors': errors
    }
    
    return jsonify(response), 200 if inserted_count > 0 else 400

@app.route('/api/stats')
def get_stats():
    """Endpoint pour les statistiques"""
    stats = {
        'total': db.get_log_count(),
        'levels': db.get_logs_by_level(),
        'top_applications': db.get_top_applications(5),
        'recent_errors': db.get_recent_errors(5)
    }
    return jsonify(stats)

def initialize_db(db_type='sqlite'):
    """Initialise la connexion à la base de données"""
    global db
    db = get_db_handler(db_type)
    db.init_db()
    print(f"✅ Database initialized ({db_type})")

def main():
    # Configuration via arguments CLI
    parser = argparse.ArgumentParser(description='LogsApp Server')
    parser.add_argument('--dbtype', choices=['sqlite', 'mysql', 'mongodb'], 
                      default='sqlite', help='Type de base de données')
    parser.add_argument('--host', default='0.0.0.0', help='Adresse IP du serveur')
    parser.add_argument('--port', type=int, default=5000, help='Port du serveur')
    parser.add_argument('--debug', action='store_true', help='Mode debug')
    
    args = parser.parse_args()
    
    # Initialisation
    initialize_db(args.dbtype)
    
    # Lancement du serveur
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug
    )

if __name__ == '__main__':
    main()