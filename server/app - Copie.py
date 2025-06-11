import argparse
from flask import Flask, request, jsonify, render_template
from db_factory import get_db_handler

app = Flask(__name__)

db = None

@app.route('/')
def index():
    tag_filter = request.args.get('tag', '')
    level_filter = request.args.get('level', '')
    logs = db.get_logs(tag=tag_filter, level=level_filter)
    return render_template('index.html', logs=logs, tag_filter=tag_filter, level_filter=level_filter)

@app.route('/receive_logs', methods=['POST'])
def receive_logs():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON received'}), 400
    tag = data.get('tag')
    logs = data.get('logs')
    if not tag or not logs:
        return jsonify({'error': 'Missing tag or logs'}), 400
    count = 0
    for log in logs:
        try:
            db.insert_log(tag, log['timestamp'], log['level'], log['message'])
            count += 1
        except Exception as e:
            print(f"Failed to insert log: {e}")
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

