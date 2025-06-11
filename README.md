# Log central bot


# 🛠️ **Projet : Centralisateur Universel de Logs Multi-Architecture avec Interface Web**

---

## 🎯 Objectif

Créer une solution de centralisation de logs **modulaire** et **multi-base** :

* Envoi périodique (toutes les 5 min) de logs taggés (FRONT, API, BACK...)
* Analyse et validation des formats
* Enregistrement dans une base de données : `SQLite` (local), `MySQL` ou `MongoDB`
* Visualisation Web moderne avec recherche/filtres

---

## 🗂️ Exemple de ligne de log attendue

Format strict :

```
2025-06-11 13:00:00  INFO Paiement validé pour l’utilisateur
```

---

## 🧠 Architecture générale

**Composants :**

1. **Client Python (log\_sender.py)**
   → Lit les logs, les filtre par format, ajoute un `tag`, et les envoie toutes les 5 minutes via API

2. **Serveur Flask (app.py)**
   → Reçoit les logs sur `/receive_logs`, choisit la base (`SQLite`, `MySQL`, ou `MongoDB`) selon config, les enregistre

3. **Interface Web**
   → Route `/` qui permet de visualiser, filtrer, trier les logs par date, niveau, tag

---

## 📋 Backlog fonctionnel

| ID | Fonctionnalité                     | Description                                                        | Priorité |
| -- | ---------------------------------- | ------------------------------------------------------------------ | -------- |
| F1 | Envoi automatique toutes les 5 min | Lecture de fichiers journaliers et envoi régulier                  | ⭐⭐⭐⭐     |
| F2 | Vérification format log            | Ne garder que les lignes valides (template fixe)                   | ⭐⭐⭐⭐     |
| F3 | Ajout de tag                       | Paramètre CLI (FRONT\_WEB, API\_AUTH, etc.) envoyé avec chaque log | ⭐⭐⭐⭐     |
| F4 | Choix base de données              | En paramètre au serveur : SQLite, MySQL, MongoDB                   | ⭐⭐⭐⭐     |
| F5 | Affichage Web                      | Interface responsive avec filtres : tag, date, niveau              | ⭐⭐⭐⭐     |
| F6 | Coloration niveau                  | INFO (vert), ERROR (rouge), WARNING (orange)                       | ⭐⭐⭐      |
| F7 | Clé API facultative                | Sécuriser les POST avec une clé partagée                           | ⭐⭐       |

---

## 🛠️ Backlog technique

| ID | Tâche technique           | Description                                                           | Priorité |
| -- | ------------------------- | --------------------------------------------------------------------- | -------- |
| T1 | Lecture fichiers logs     | Parser les logs et ne lire que les nouvelles lignes                   | ⭐⭐⭐⭐     |
| T2 | Validation RegEx          | Valider chaque ligne avec `YYYY-MM-DD HH:MM:SS LEVEL Message`         | ⭐⭐⭐⭐     |
| T3 | API Flask `/receive_logs` | Acceptation de POST JSON (logs + tag)                                 | ⭐⭐⭐⭐     |
| T4 | Interface `/`             | Flask + Jinja2 + Bootstrap avec filtres dynamiques                    | ⭐⭐⭐⭐     |
| T5 | Drivers SQL et NoSQL      | Support SQLAlchemy (MySQL, SQLite) et PyMongo pour MongoDB            | ⭐⭐⭐⭐     |
| T6 | Abstraction DB            | Interface commune pour `insert_log()`, `get_logs()` etc.              | ⭐⭐⭐⭐     |
| T7 | Cron client               | Boucle toutes les 5 minutes, lecture du fichier `logs-YYYY-MM-DD.txt` | ⭐⭐⭐⭐     |

---

## 🧾 Paramètres en ligne de commande

### 🎯 Client :

```bash
python log_sender.py --tag API_BILLING --logfile logs-2025-06-11.txt --server http://localhost:5000
```

### 🎯 Serveur :

```bash
python app.py --dbtype sqlite    # ou mysql ou mongodb
```

---

## 🧬 Arborescence du projet

```
log_centralizer/
├── client/
│   └── log_sender.py                # Client d'envoi de logs avec filtrage + intervalle 5 min
│
├── server/
│   ├── app.py                       # Application Flask (serveur Web + API)
│   ├── config.py                    # Configuration selon le type de base (MySQL, MongoDB, SQLite)
│   ├── db_factory.py                # Fabrique de DB : instancie le bon backend
│   ├── db_sqlite.py                 # Backend SQLite
│   ├── db_mysql.py                  # Backend MySQL
│   ├── db_mongo.py                  # Backend MongoDB
│   ├── templates/
│   │   └── index.html               # Interface utilisateur Web
│   └── static/
│       └── style.css                # Design CSS personnalisé (Bootstrap étendu)
│
├── logs-2025-06-11.txt              # Exemple de fichier log local (client)
├── requirements.txt                 # Dépendances : Flask, pymongo, mysql-connector-python, etc.
└── README.md                        # Documentation + instructions de lancement
```

---

## 🔁 Support multibase via `db_factory.py`

```python
# db_factory.py
def get_db_handler(dbtype):
    if dbtype == 'sqlite':
        from db_sqlite import SQLiteHandler
        return SQLiteHandler()
    elif dbtype == 'mysql':
        from db_mysql import MySQLHandler
        return MySQLHandler()
    elif dbtype == 'mongodb':
        from db_mongo import MongoHandler
        return MongoHandler()
    else:
        raise ValueError("Unsupported database type")
```

---

## 🚀 Étapes suivantes

Souhaites-tu que je génère **tout le code** pour :

1. `log_sender.py`
2. `app.py` + interface HTML
3. `db_sqlite.py`, `db_mysql.py`, `db_mongo.py`
4. Base de données test (SQLite + MySQL)
5. Un `Dockerfile` optionnel pour l’exécution standardisée

✋ Dis-moi par quoi tu veux commencer, ou si tu veux **le starter complet directement prêt à l’emploi**.
