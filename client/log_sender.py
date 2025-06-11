import argparse
import re
import time
import requests
from datetime import datetime

LOG_PATTERN = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+(INFO|ERROR|WARNING)\s+(.*)$')

def parse_logs(file_path, last_pos=0):
    logs = []
    with open(file_path, 'r', encoding='utf-8') as f:
        f.seek(last_pos)
        for line in f:
            line = line.strip()
            if not line:
                continue
            m = LOG_PATTERN.match(line)
            if m:
                timestamp_str, level, message = m.groups()
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                logs.append({
                    'timestamp': timestamp_str,
                    'level': level,
                    'message': message
                })
            else:
                print(f"Ignored invalid log line: {line}")
        last_pos = f.tell()
    return logs, last_pos

def main():
    parser = argparse.ArgumentParser(description="Log sender client")
    parser.add_argument('--tag', required=True, help='Tag d’architecture du client (ex: FRONT_WEB)')
    parser.add_argument('--logfile', required=True, help='Chemin fichier log journalier')
    parser.add_argument('--server', required=True, help='URL du serveur (ex: http://localhost:5000)')
    parser.add_argument('--interval', type=int, default=300, help='Intervalle d’envoi en secondes (default 300)')
    args = parser.parse_args()

    last_pos = 0
    print(f"Client started with tag={args.tag} sending logs from {args.logfile} every {args.interval}s")
    while True:
        try:
            logs, last_pos = parse_logs(args.logfile, last_pos)
            if logs:
                payload = {
                    'tag': args.tag,
                    'logs': logs
                }
                response = requests.post(f"{args.server}/receive_logs", json=payload)
                if response.status_code == 200:
                    print(f"Sent {len(logs)} logs successfully")
                else:
                    print(f"Failed to send logs: {response.status_code} - {response.text}")
            else:
                print("No new valid logs to send")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(args.interval)

if __name__ == '__main__':
    main()

