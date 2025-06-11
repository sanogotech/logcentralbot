
# 📊 Centralisateur de Logs

Centralisateur léger de logs permettant d'envoyer, stocker et visualiser les journaux depuis diverses applications (Web, Mobile, Backend, etc.) avec filtres par `tag` et `niveau`.

---

## ✨ Fonctionnalités

- 🔌 Envoi de logs via HTTP (GET)
- 🧾 Stockage dans SQLite, MySQL ou MongoDB
- 🧠 Filtrage des logs par `tag` et `niveau` (`INFO`, `WARNING`, `ERROR`)
- 📺 Interface web de visualisation (Bootstrap 5)
- ⚙️ Configuration facile via ligne de commande
- 🧪 Structure TDD-ready pour évolutions futures

---

## 📁 Structure du projet

```

centralisateur-logs/
│
├── client/                    # Client Python d'envoi de logs
│   └── log\_sender.py
│
├── server/                    # Serveur Flask de réception/affichage
│   ├── app.py
│   ├── storage/
│   │   ├── **init**.py
│   │   ├── sqlite\_storage.py
│   │   ├── mysql\_storage.py
│   │   └── mongo\_storage.py
│   └── templates/
│       └── logs.html          # Interface web
│
├── requirements.txt           # Dépendances
└── README.md                  # Ce fichier

````

---

## 🚀 Démarrage rapide

### 1. Installation des dépendances

```bash
pip install -r requirements.txt
````

### 2. Lancement du serveur

```bash
python server/app.py --dbtype=sqlite
```

Options disponibles :

* `--dbtype=sqlite` (défaut)
* `--dbtype=mysql`
* `--dbtype=mongo`

Pour MySQL/MongoDB, veillez à configurer les identifiants dans `app.py`.

### 3. Envoi de logs (Client)

```bash
python client/log_sender.py \
  --tag=FRONT_WEB \
  --logfile=/chemin/vers/fichier.log \
  --server=http://localhost:5000 \
  --interval=300
```

Paramètres :

* `--tag` : Identifiant de l'application émettrice
* `--logfile` : Fichier journal à suivre
* `--server` : URL du serveur Flask
* `--interval` : Intervalle d’envoi en secondes

---

## 🌐 Interface Web

Accessible à : [http://localhost:5000](http://localhost:5000)

Fonctionnalités :

* Recherche par tag
* Filtrage par niveau (`INFO`, `WARNING`, `ERROR`)
* Tableau dynamique avec Bootstrap

---

## 🔧 Exemple de log accepté

Format de log accepté dans le fichier :

```
[2025-06-11 12:34:56] [ERROR] Une erreur est survenue dans le service utilisateur.
```

---

## 🐳 Docker (Optionnel)

Tu peux dockeriser ce projet facilement. Exemple de `Dockerfile` et `docker-compose.yml` fournis sur demande.

---

## 🧪 Tests et développement futur

Architecture modulaire conçue pour :

* Ajout de nouveaux backends de stockage
* Tests unitaires (TDD-ready)
* Intégration CI/CD

---

## 🧩 Technologies utilisées

* Python 3.10+
* Flask
* SQLite / MySQL / MongoDB
* Bootstrap 5
* Requests

---

## 📜 Licence

Ce projet est sous licence MIT – voir le fichier [LICENSE](LICENSE) pour plus d’informations.

---

## 🙋‍♂️ Auteur

Développé par \[TonNom].

Pour toute contribution, ouverture d'issue ou amélioration, les PR sont les bienvenues !

---

## 🔮 À venir

* Authentification (JWT)
* Export CSV/JSON des logs
* Alertes email ou webhook
* Dashboard de statistiques

```

---

Souhaites-tu aussi que je t’ajoute :

- un exemple de `Dockerfile` + `docker-compose.yml` ?
- un badge CI (GitHub Actions) ?
- une version anglaise du README ?

