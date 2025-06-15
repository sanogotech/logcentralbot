import argparse
import re
import time
import requests
from datetime import datetime

# Expression régulière pour parser les lignes de log
LOG_PATTERN = re.compile(
    r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+(INFO|WARNING|ERROR)\s+(.+)$'
)

# Expression régulière pour extraire le temps de réponse
RESPONSE_TIME_PATTERN = re.compile(r'\[RT:(\d+)ms\]')


def parse_logs(file_path, last_pos=0, context=None):
    """Parse le fichier de logs et extrait les entrées valides"""
    logs = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.seek(last_pos)
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Extraire le temps de réponse si présent
                rt_match = RESPONSE_TIME_PATTERN.search(line)
                response_time = int(rt_match.group(1)) if rt_match else None
                
                # Parser la ligne de log
                m = LOG_PATTERN.match(line)
                if m:
                    timestamp_str, level, message = m.groups()
                    try:
                        # Nettoyer le message en supprimant les parties entre crochets
                        clean_msg = re.sub(r'\[.*?\]', '', message).strip()
                        
                        log_entry = {
                            'application': context['application'],
                            'tag': context['tag'],
                            'timestamp': timestamp_str,
                            'level': level,
                            'message': clean_msg,  # Utiliser le message nettoyé
                            'user': context['user'],
                            'module': context['module'],
                            'host': context['host'],
                            'response_time': response_time
                        }
                        logs.append(log_entry)
                    except ValueError:
                        continue
            last_pos = f.tell()
    except Exception as e:
        print(f"Error reading log file: {e}")
    return logs, last_pos
    


def send_logs(server_url, logs):
    """Envoie les logs au serveur"""
    try:
        response = requests.post(
            f"{server_url}/receive_logs",
            json={'logs': logs},
            timeout=5
        )
        if response.status_code == 200:
            print(f"Successfully sent {len(logs)} logs")
            return True
        else:
            print(f"Server returned {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send logs: {e}")
    return False

def main():
    parser = argparse.ArgumentParser(description="Client d'envoi de logs")
    
    # Arguments obligatoires
    parser.add_argument('--application', required=True, help="Nom de l'application")
    parser.add_argument('--tag', required=True, help="Tag fonctionnel (ex: API, AUTH)")
    parser.add_argument('--logfile', required=True, help="Chemin du fichier de logs")
    parser.add_argument('--server', required=True, help="URL du serveur (ex: http://localhost:5000)")
    
    # Arguments optionnels
    parser.add_argument('--user', default='system', help="Utilisateur associé")
    parser.add_argument('--module', default='main', help="Module concerné")
    parser.add_argument('--host', default='localhost', help="Host d'origine")
    parser.add_argument('--interval', type=int, default=60, help="Intervalle d'envoi en secondes")

    args = parser.parse_args()
    
    context = {
        'application': args.application,
        'tag': args.tag,
        'user': args.user,
        'module': args.module,
        'host': args.host
    }

    last_pos = 0
    print(f"Démarrage du monitoring de {args.logfile}...")

    while True:
        logs, last_pos = parse_logs(args.logfile, last_pos, context)
        if logs:
            send_logs(args.server, logs)
        time.sleep(args.interval)

if __name__ == '__main__':
    main()


################################################################
# Exemples d'appel en ligne de commande :
################################################################

# 1. Surveillance basique d'une application web :
# python client/log_sender.py --application "API-Gateway" --tag "REST-API" --logfile "logs-2025-06-15Complet.txt" --server " http://localhost:5000" --user "api-service" --module "Authentication" --host "api-server-01" --interval 5
# python log_sender.py --application WebApp --tag FRONTEND --logfile /var/log/webapp.log --server http://monitoring.example.com

# 2. Surveillance avec utilisateur spécifique et intervalle rapide :
# python log_sender.py --application PaymentService --tag STRIPE --logfile /logs/payments.log --server http://localhost:5000 --user payment-worker --module Gateway --interval 10

# 3. Surveillance d'un serveur spécifique avec tag personnalisé :
# python log_sender.py --application Database --tag BACKUP --logfile /mnt/logs/db_backup.log --server http://log-aggregator.internal --host db-server-01 --module BackupService