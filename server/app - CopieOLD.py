import argparse
from flask import Flask, request, jsonify, render_template
from db_factory import get_db_handler

app = Flask(__name__)
db = None

@app.route('/')
def index():
    tag_filter = request.args.get('tag', '')
    level_filter = request.args.get('level', '')
    application_filter = request.args.get('application', '')
    logs = db.get_logs(tag=tag_filter, level=level_filter, application=application_filter)
    return render_template('index.html', logs=logs, tag_filter=tag_filter,
                           level_filter=level_filter, application_filter=application_filter)

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
                timestamp=log['timestamp'],
                level=log['level'],
                message=log['message'],
                user=log.get('user', 'system'),
                module=log.get('module', 'main'),
                host=log.get('host', 'localhost')
            )
            count += 1
        except Exception as e:
            print(f"❌ Failed to insert log: {e}")
    return jsonify({'message': f'{count} logs inserted'}), 200

def main():
    global db
    parser = argparse.ArgumentParser()
    parser.add_argument('--dbtype', choices=['sqlite', 'mysql', 'mongodb'], default='sqlite', help='Type de base de données')
    args = parser.parse_args()

    db = get_db_handler(args.dbtype)
    db.init_db()

    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main()

