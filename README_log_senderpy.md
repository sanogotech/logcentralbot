# 📘 README — Client `log_sender.py`

### 📌 Description

`log_sender.py` est un client Python simple mais puissant conçu pour surveiller un fichier de logs en continu, extraire les lignes valides, les enrichir avec des métadonnées contextuelles (comme le nom de l’application, le module, l’utilisateur, etc.), et les envoyer périodiquement à un serveur central via une API HTTP.

---

### ⚙️ Commande de lancement

```bash
python log_sender.py \
  --application MyApp \
  --tag FRONT_WEB \
  --logfile /path/to/myapp.log \
  --server http://localhost:5000 \
  --user alice \
  --module AuthService \
  --host 192.168.1.100 \
  --interval 60
```

---

### 🧩 Paramètres détaillés

| Paramètre       | Obligatoire | Description                                                                                                                                                                              |
| --------------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--application` | ✅ Oui       | **Nom logique de l’application** (ex : `CRM`, `Billing`, `Monitoring`). Permet à la plateforme serveur de classer les logs par application. <br>👉 *Ex :* `--application BillingService` |
| `--tag`         | ✅ Oui       | **Tag fonctionnel** indiquant le rôle ou composant (ex : `FRONT_WEB`, `API_BACKEND`, `MOBILE_APP`). <br>👉 *Ex :* `--tag API_BACKEND`                                                    |
| `--logfile`     | ✅ Oui       | **Chemin absolu ou relatif du fichier de log** à surveiller. Le client suit ce fichier et envoie les nouvelles lignes valides. <br>👉 *Ex :* `--logfile /var/log/myapp/access.log`       |
| `--server`      | ✅ Oui       | **URL complète du serveur** recevant les logs. <br>👉 *Ex :* `--server http://localhost:5000`                                                                                            |
| `--user`        | ❌ Non       | **Nom de l’utilisateur ou service** ayant généré les logs. Par défaut `system`. <br>👉 *Ex :* `--user admin123`                                                                          |
| `--module`      | ❌ Non       | **Nom du module ou sous-système** (ex : `Login`, `Payment`, `DBSync`) qui produit les logs. Par défaut `main`. <br>👉 *Ex :* `--module UserController`                                   |
| `--host`        | ❌ Non       | **Nom ou adresse IP de la machine émettrice**. Par défaut `localhost`. <br>👉 *Ex :* `--host srv-log-01`                                                                                 |
| `--interval`    | ❌ Non       | **Intervalle en secondes entre deux envois** de logs au serveur. Par défaut `300`. <br>👉 *Ex :* `--interval 60`                                                                         |

---

### 🧪 Exemples d’utilisation

#### 1. Pour une application web

```bash
python log_sender.py \
  --application Website \
  --tag FRONT_WEB \
  --logfile logs/web.log \
  --server http://10.0.0.1:5000 \
  --user www-data \
  --module Router \
  --host web01 \
  --interval 30
```

#### 2. Pour une application mobile Android

```bash
python log_sender.py \
  --application MobileApp \
  --tag MOBILE_ANDROID \
  --logfile /logs/app_android.log \
  --server http://log-server:5000 \
  --user system \
  --module SyncService \
  --host mobile-emulator \
  --interval 60
```

#### 3. Pour un microservice

```bash
python log_sender.py \
  --application InventoryService \
  --tag API_BACKEND \
  --logfile /opt/logs/inventory.log \
  --server http://localhost:5000 \
  --user inventory-bot \
  --module StockUpdater \
  --host api-node-1 \
  --interval 10
```

---

### 📤 Format JSON envoyé au serveur

Chaque ligne de log conforme sera envoyée sous forme d’un dictionnaire enrichi :

```json
{
  "logs": [
    {
      "application": "CRM",
      "tag": "API_BACKEND",
      "timestamp": "2025-06-11 08:00:00",
      "level": "INFO",
      "message": "User login successful",
      "user": "admin",
      "module": "LoginService",
      "host": "server01"
    },
    ...
  ]
}
```

---

### 🧪 Format attendu des lignes dans le fichier de logs

Seules les lignes respectant ce format seront reconnues :

```
YYYY-MM-DD HH:MM:SS LEVEL message
```

Exemples valides :

```
2025-06-11 08:00:00 INFO User logged in
2025-06-11 08:05:12 ERROR Connection failed
```

Exemples ignorés :

```
INVALID LINE
[INFO] Startup complete
```

---

### 🚀 Astuces d’usage

* Intégrez ce client dans un `systemd` service ou un `cron` pour automatiser son exécution.
* Combinez avec un outil comme **Filebeat** si vous voulez une version plus robuste avec buffering.
* Utilisez un reverse proxy type **nginx** devant le serveur pour sécuriser les communications avec HTTPS.

---

Souhaites-tu maintenant que je génère un `README.md` prêt à l'emploi, ou que je t’aide à modifier le serveur (`Flask`) pour qu’il stocke ces nouveaux champs ?
