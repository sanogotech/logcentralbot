import argparse
from datetime import datetime  # Import manquant
from flask import Flask, request, jsonify, render_template
from db_factory import get_db_handler

app = Flask(__name__)
db = None

@app.route('/')
def index():
    # Récupère tous les paramètres de filtrage
    filters = {
        'tag': request.args.get('tag', ''),
        'level': request.args.get('level', ''),
        'application': request.args.get('application', ''),
        'module': request.args.get('module', ''),
        'host': request.args.get('host', '')
    }
    
    # Récupère les logs filtrés
    logs = db.get_logs(**filters)
    
    return render_template(
        'index.html',
        logs=logs,
        **filters,
        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

@app.route('/receive_logs', methods=['POST'])
def receive_logs():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON received'}), 400

    logs = data.get('logs', [])
    if not logs:
        return jsonify({'error': 'No logs provided'}), 400

    count = 0
    for log in logs:
        try:
            db.insert_log(
                application=log.get('application', 'Unknown'),
                tag=log.get('tag', 'Unknown'),
                timestamp=log.get('timestamp', ''),
                level=log.get('level', 'INFO'),
                message=log.get('message', ''),
                user=log.get('user', 'system'),
                module=log.get('module', 'main'),
                host=log.get('host', 'localhost')
            )
            count += 1
        except Exception as e:
            print(f"❌ Failed to insert log: {e}")
    return jsonify({'message': f'{count} logs inserted'}), 200


@app.route('/bam_metrics')
def bam_metrics():
    # Endpoint pour les données BAM (à implémenter)
    return jsonify({
        "kpis": [
            {"name": "Taux de transactions", "value": "98.5%", "target": ">95%"},
            {"name": "Erreurs de paiement", "value": "12/h", "target": "<20/h"}
        ],
        "alerts": [
            {"message": "⚠️ Taux de conversion en baisse de 15%", "timestamp": "2023-11-15 14:30"}
        ]
    })

def main():
    global db
    parser = argparse.ArgumentParser()
    parser.add_argument('--dbtype', choices=['sqlite', 'mysql', 'mongodb'], 
                      default='sqlite', help='Type de base de données')
    args = parser.parse_args()

    db = get_db_handler(args.dbtype)
    db.init_db()

    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main()
