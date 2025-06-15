import argparse
import re
import time
import requests
from datetime import datetime

# python log_sender.py  --application CRM_App --tag FRONT_WEB  --logfile /var/log/crm.log --server http://localhost:5000 --user johndoe --module LoginService --host 192.168.1.20 --interval 60

# python client/log_sender.py  --application CRM_App --tag FRONT_WEB  --logfile logs-2025-06-11.txt --server http://localhost:5000 --user johndoe --module LoginService --host 192.168.1.20 --interval 60

# Expression régulière robuste pour capturer les lignes de log valides
LOG_PATTERN = re.compile(
    r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+(INFO|ERROR|WARNING)\s+(.+)$'
)

def parse_logs(file_path, last_pos=0, context=None):
    logs = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.seek(last_pos)
            for line in f:
                original_line = line
                line = line.strip()
                if not line:
                    continue
                m = LOG_PATTERN.match(line)
                if m:
                    timestamp_str, level, message = m.groups()
                    try:
                        datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                        log_entry = {
                            'application': context['application'],
                            'tag': context['tag'],
                            'timestamp': timestamp_str,
                            'level': level,
                            'message': message,
                            'user': context['user'],
                            'module': context['module'],
                            'host': context['host']
                        }
                        logs.append(log_entry)
                    except ValueError as ve:
                        print(f"Invalid timestamp in line: {repr(original_line)} — {ve}")
                else:
                    print(f"Ignored invalid log line: {repr(original_line)}")
            last_pos = f.tell()
    except Exception as e:
        print(f"Error reading log file: {e}")
    return logs, last_pos

def send_logs(server_url, logs):
    try:
        response = requests.post(f"{server_url}/receive_logs", json={'logs': logs})
        if response.status_code == 200:
            print(f"✅ Sent {len(logs)} logs successfully")
        else:
            print(f"❌ Failed to send logs: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"🚨 Network error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Client d’envoi de logs enrichis")
    parser.add_argument('--application', required=True, help='Nom de l’application')
    parser.add_argument('--tag', required=True, help='Tag du client (ex: FRONT_WEB)')
    parser.add_argument('--logfile', required=True, help='Fichier de log à surveiller')
    parser.add_argument('--server', required=True, help='URL du serveur (ex: http://localhost:5000)')
    parser.add_argument('--user', default='system', help='Utilisateur générant les logs')
    parser.add_argument('--module', default='main', help='Nom du module (ex: AuthService)')
    parser.add_argument('--host', default='localhost', help='Nom ou IP de la machine')
    parser.add_argument('--interval', type=int, default=300, help='Intervalle d’envoi en secondes')

    args = parser.parse_args()

    context = {
        'application': args.application,
        'tag': args.tag,
        'user': args.user,
        'module': args.module,
        'host': args.host
    }

    last_pos = 0
    print(f"📡 Client started for application={args.application}, tag={args.tag}, sending logs from {args.logfile} every {args.interval}s")

    while True:
        logs, last_pos = parse_logs(args.logfile, last_pos, context)
        if logs:
            send_logs(args.server, logs)
        else:
            print("ℹ️ No new valid logs to send")
        time.sleep(args.interval)

if __name__ == '__main__':
    main()
