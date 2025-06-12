# **Top 40 des Requêtes SQL pour un Système de Centralisation de Logs**

## **Catégorisation par Type d'Information**

### **1. Requêtes pour le Monitoring Technique**
#### **a. Statistiques Basiques**
1. **Volume de logs par niveau**  
   ```sql
   SELECT level, COUNT(*) as count 
   FROM logs 
   GROUP BY level;
   ```
   *Usage*: Dashboard technique.

2. **Logs par application**  
   ```sql
   SELECT application, COUNT(*) as count 
   FROM logs 
   GROUP BY application 
   ORDER BY count DESC;
   ```

3. **Top 10 des tags les plus fréquents**  
   ```sql
   SELECT tag, COUNT(*) as count 
   FROM logs 
   WHERE tag IS NOT NULL 
   GROUP BY tag 
   ORDER BY count DESC 
   LIMIT 10;
   ```

#### **b. Analyse Temporelle**
4. **Logs par heure/jour**  
   ```sql
   SELECT strftime('%Y-%m-%d %H:00', timestamp) as hour, COUNT(*) 
   FROM logs 
   GROUP BY hour;
   ```

5. **Évolution des erreurs sur 7 jours**  
   ```sql
   SELECT DATE(timestamp) as day, COUNT(*) 
   FROM logs 
   WHERE level = 'ERROR' 
   AND timestamp >= DATE('now', '-7 days') 
   GROUP BY day;
   ```

6. **Heures de pointe pour les erreurs**  
   ```sql
   SELECT strftime('%H:00', timestamp) as hour, COUNT(*) 
   FROM logs 
   WHERE level = 'ERROR' 
   GROUP BY hour 
   ORDER BY COUNT(*) DESC;
   ```

### **2. Requêtes pour le BAM (Business Activity Monitoring)**
#### **a. KPI Métiers**
7. **Taux de transactions réussies**  
   ```sql
   SELECT 
     (COUNT(CASE WHEN tag = 'checkout_success' THEN 1 END) * 100.0 / 
      COUNT(CASE WHEN tag IN ('checkout_success', 'checkout_error') THEN 1 END)) as success_rate
   FROM logs;
   ```

8. **Erreurs de paiement par heure**  
   ```sql
   SELECT strftime('%Y-%m-%d %H:00', timestamp) as hour, COUNT(*) 
   FROM logs 
   WHERE tag = 'payment_error' 
   GROUP BY hour;
   ```

9. **Temps moyen de réponse API**  
   ```sql
   SELECT AVG(CAST(json_extract(message, '$.response_time') AS FLOAT)) 
   FROM logs 
   WHERE tag = 'api_response';
   ```

#### **b. Détection d'Anomalies**
10. **Spikes d'erreurs**  
    ```sql
    SELECT application, COUNT(*) as error_count 
    FROM logs 
    WHERE level = 'ERROR' 
    AND timestamp >= DATETIME('now', '-1 hour') 
    GROUP BY application 
    HAVING error_count > 20;
    ```

11. **Services les plus lents**  
    ```sql
    SELECT module, AVG(CAST(json_extract(message, '$.response_time') AS FLOAT) as avg_time 
    FROM logs 
    WHERE tag = 'api_response' 
    GROUP BY module 
    ORDER BY avg_time DESC 
    LIMIT 5;
    ```

### **3. Requêtes pour la Sécurité**
12. **Tentatives de connexion échouées**  
    ```sql
    SELECT user, COUNT(*) as failed_attempts 
    FROM logs 
    WHERE tag = 'auth_failed' 
    GROUP BY user 
    ORDER BY failed_attempts DESC 
    LIMIT 10;
    ```

13. **Activité suspecte par IP**  
    ```sql
    SELECT host, COUNT(*) as events 
    FROM logs 
    WHERE level = 'WARNING' 
    GROUP BY host 
    ORDER BY events DESC 
    LIMIT 5;
    ```

### **4. Requêtes pour l'Optimisation**
14. **Logs les plus volumineux**  
    ```sql
    SELECT id, LENGTH(message) as size 
    FROM logs 
    ORDER BY size DESC 
    LIMIT 10;
    ```

15. **Tags inutilisés**  
    ```sql
    SELECT tag, COUNT(*) as count 
    FROM logs 
    GROUP BY tag 
    HAVING count < 5;
    ```

---

## **Actions pour le Client (Log Sender)**

### **1. Optimisation des Envois**
- **Enrichir les logs** avec des métadonnées structurées :  
  ```json
  {
    "timestamp": "2025-06-12 14:30:00",
    "level": "ERROR",
    "tag": "payment_error",
    "message": "Timeout processing payment",
    "metadata": {
      "transaction_id": "tx_123",
      "amount": 150.00,
      "user_id": "usr_456"
    }
  }
  ```
- **Utiliser des batches** pour réduire le nombre de requêtes HTTP.

### **2. Meilleures Pratiques**
- **Éviter les logs trop verbeux** (ex: stack traces complètes sans contexte).  
- **Taguer systématiquement** les logs (ex: `checkout`, `auth`, `api`).  
- **Configurer des niveaux de log appropriés** (DEBUG, INFO, ERROR).  

### **3. Exemple de Configuration Idéale**
```python
# Dans log_sender.py
log_entry = {
    "application": "checkout_service",
    "tag": "payment_error",  # → Permet des requêtes SQL ciblées
    "timestamp": datetime.now().isoformat(),
    "level": "ERROR",
    "message": json.dumps({
        "error": "Payment gateway timeout",
        "transaction_id": "tx_123",
        "user_id": "usr_456"
    }),
    "user": "johndoe",
    "host": "192.168.1.10"
}
```

---

## **Résumé des Bonnes Pratiques**
| **Catégorie**       | **Action Clé**                                  | **Impact**                          |
|---------------------|-----------------------------------------------|------------------------------------|
| **Structured Logs** | Utiliser JSON pour les messages complexes.     | Meilleure analyse via SQL.         |
| **Tagging**         | Appliquer des tags cohérents (ex: `api_health`). | Filtrage efficace.                 |
| **Volume Control**  | Limiter les logs DEBUG en production.          | Réduction des coûts de stockage.   |
| **Batching**        | Envoyer les logs par groupes de 100.           | Optimisation réseau/performance.   |

Ces requêtes et bonnes pratiques permettent de transformer un système de logs en **outil puissant pour la technique, le métier et la sécurité**.

# **Top 80 Requêtes SQL pour un Système de Logs**  
*(20 requêtes par catégorie : Techniques, Métier, Sécurité, Optimisation)*  

---

## **1. Requêtes Techniques** *(Monitoring & Debug)*  

### **Statistiques Basiques**  
1. **Volume de logs par niveau**  
   ```sql
   SELECT level, COUNT(*) as count FROM logs GROUP BY level;
   ```

2. **Logs par application**  
   ```sql
   SELECT application, COUNT(*) as count FROM logs GROUP BY application ORDER BY count DESC;
   ```

3. **Top 10 des tags les plus fréquents**  
   ```sql
   SELECT tag, COUNT(*) as count FROM logs WHERE tag IS NOT NULL GROUP BY tag ORDER BY count DESC LIMIT 10;
   ```

4. **Logs sans tag**  
   ```sql
   SELECT COUNT(*) as untagged_logs FROM logs WHERE tag IS NULL OR tag = '';
   ```

### **Analyse Temporelle**  
5. **Logs par heure**  
   ```sql
   SELECT strftime('%Y-%m-%d %H:00', timestamp) as hour, COUNT(*) 
   FROM logs GROUP BY hour;
   ```

6. **Évolution des erreurs sur 7 jours**  
   ```sql
   SELECT DATE(timestamp) as day, COUNT(*) 
   FROM logs WHERE level = 'ERROR' AND timestamp >= DATE('now', '-7 days') 
   GROUP BY day;
   ```

7. **Heures de pointe pour les erreurs**  
   ```sql
   SELECT strftime('%H:00', timestamp) as hour, COUNT(*) 
   FROM logs WHERE level = 'ERROR' GROUP BY hour ORDER BY COUNT(*) DESC;
   ```

8. **Activité nocturne anormale**  
   ```sql
   SELECT strftime('%H:00', timestamp) as hour, COUNT(*) 
   FROM logs WHERE CAST(strftime('%H', timestamp) AS INTEGER) BETWEEN 0 AND 5 
   GROUP BY hour;
   ```

### **Performances**  
9. **Top 5 des modules les plus lents**  
   ```sql
   SELECT module, AVG(response_time) as avg_time 
   FROM logs WHERE tag = 'api_response' 
   GROUP BY module ORDER BY avg_time DESC LIMIT 5;
   ```

10. **Services avec temps de réponse > 1s**  
    ```sql
    SELECT module, COUNT(*) as slow_requests 
    FROM logs WHERE json_extract(message, '$.response_time') > 1000 
    GROUP BY module;
    ```

11. **Latence 95e percentile**  
    ```sql
    SELECT module, response_time 
    FROM logs WHERE tag = 'api_response' 
    ORDER BY response_time DESC LIMIT 1 OFFSET (
      SELECT COUNT(*) FROM logs WHERE tag = 'api_response'
    ) * 5 / 100;
    ```

### **Erreurs Système**  
12. **Erreurs par type**  
    ```sql
   SELECT json_extract(message, '$.error_type') as error_type, COUNT(*) 
   FROM logs WHERE level = 'ERROR' GROUP BY error_type;
   ```

13. **Erreurs récurrentes**  
    ```sql
    SELECT message, COUNT(*) as occurrences 
    FROM logs WHERE level = 'ERROR' 
    GROUP BY message HAVING occurrences > 5;
    ```

14. **Erreurs non résolues (reapparues dans les 24h)**  
    ```sql
    SELECT message, COUNT(DISTINCT DATE(timestamp)) as days 
    FROM logs WHERE level = 'ERROR' 
    GROUP BY message HAVING days > 1;
    ```

### **Connexions & Réseau**  
15. **Connexions actives par host**  
    ```sql
    SELECT host, COUNT(*) as connections 
    FROM logs WHERE tag = 'connection' 
    GROUP BY host ORDER BY connections DESC;
    ```

16. **Déconnexions inattendues**  
    ```sql
    SELECT host, COUNT(*) as unexpected_disconnects 
    FROM logs WHERE tag = 'connection' AND message LIKE '%unexpected%' 
    GROUP BY host;
    ```

17. **Top 10 des IPs les plus actives**  
    ```sql
    SELECT host, COUNT(*) as requests 
    FROM logs WHERE host LIKE '%.%.%.%' 
    GROUP BY host ORDER BY requests DESC LIMIT 10;
    ```

### **Capacité & Stockage**  
18. **Taille moyenne des logs**  
    ```sql
    SELECT AVG(LENGTH(message)) as avg_size FROM logs;
    ```

19. **Logs les plus volumineux**  
    ```sql
    SELECT id, LENGTH(message) as size 
    FROM logs ORDER BY size DESC LIMIT 10;
    ```

20. **Estimation de croissance**  
    ```sql
    SELECT DATE(timestamp) as day, COUNT(*) as daily_count 
    FROM logs GROUP BY day ORDER BY day;
    ```

---

## **2. Requêtes Métier** *(BAM & KPI)*  

### **Transactions & Paiements**  
21. **Taux de transactions réussies**  
    ```sql
    SELECT 
      (COUNT(CASE WHEN tag = 'checkout_success' THEN 1 END) * 100.0 / 
      COUNT(CASE WHEN tag IN ('checkout_success', 'checkout_error') THEN 1 END)) as success_rate 
    FROM logs;
    ```

22. **Panier moyen abandonné**  
    ```sql
    SELECT AVG(CAST(json_extract(message, '$.cart_value') AS FLOAT)) 
    FROM logs WHERE tag = 'cart_abandoned';
    ```

23. **Top 5 produits en rupture**  
    ```sql
    SELECT json_extract(message, '$.product_id') as product, COUNT(*) 
    FROM logs WHERE tag = 'out_of_stock' 
    GROUP BY product ORDER BY COUNT(*) DESC LIMIT 5;
    ```

### **Utilisateurs**  
24. **Nouveaux utilisateurs/jour**  
    ```sql
    SELECT DATE(timestamp) as day, COUNT(DISTINCT user) 
    FROM logs WHERE tag = 'user_signup' 
    GROUP BY day;
    ```

25. **Taux de rétention (J+7)**  
    ```sql
    SELECT COUNT(DISTINCT a.user) * 100.0 / COUNT(DISTINCT b.user) 
    FROM logs a JOIN logs b ON a.user = b.user 
    WHERE a.tag = 'login' AND b.tag = 'signup' 
    AND DATE(a.timestamp) = DATE(b.timestamp, '+7 days');
    ```

### **Ventes & Marketing**  
26. **Conversions par campagne**  
    ```sql
    SELECT json_extract(message, '$.campaign_id') as campaign, COUNT(*) 
    FROM logs WHERE tag = 'purchase' 
    GROUP BY campaign;
    ```

27. **CA par heure**  
    ```sql
    SELECT strftime('%H:00', timestamp) as hour, 
    SUM(CAST(json_extract(message, '$.amount') AS FLOAT)) as revenue 
    FROM logs WHERE tag = 'purchase' 
    GROUP BY hour;
    ```

### **Support Client**  
28. **Tickets ouverts/jour**  
    ```sql
    SELECT DATE(timestamp) as day, COUNT(*) 
    FROM logs WHERE tag = 'support_ticket' 
    GROUP BY day;
    ```

29. **Temps moyen de résolution**  
    ```sql
    SELECT AVG((resolved_at - created_at)) as avg_resolution_time 
    FROM (
      SELECT 
        MIN(CASE WHEN message LIKE '%ticket opened%' THEN timestamp END) as created_at,
        MIN(CASE WHEN message LIKE '%ticket closed%' THEN timestamp END) as resolved_at
      FROM logs WHERE tag = 'support_ticket' 
      GROUP BY json_extract(message, '$.ticket_id')
    );
    ```

### **Logistique**  
30. **Retards de livraison**  
    ```sql
    SELECT json_extract(message, '$.carrier') as carrier, COUNT(*) 
    FROM logs WHERE tag = 'delivery_delay' 
    GROUP BY carrier;
    ```

31. **Retours clients**  
    ```sql
    SELECT json_extract(message, '$.reason') as reason, COUNT(*) 
    FROM logs WHERE tag = 'product_return' 
    GROUP BY reason;
    ```

---

## **3. Requêtes Sécurité**  

### **Authentification**  
32. **Tentatives de connexion échouées**  
    ```sql
    SELECT user, COUNT(*) as failed_attempts 
    FROM logs WHERE tag = 'auth_failed' 
    GROUP BY user ORDER BY failed_attempts DESC LIMIT 10;
    ```

33. **Attaques par force brute**  
    ```sql
    SELECT host, COUNT(*) as attempts 
    FROM logs WHERE tag = 'auth_failed' 
    AND timestamp >= DATETIME('now', '-1 hour') 
    GROUP BY host HAVING attempts > 10;
    ```

### **Activité Suspecte**  
34. **Requêtes SQL inhabituelles**  
    ```sql
    SELECT message FROM logs 
    WHERE message LIKE '%SELECT * FROM users%' 
    OR message LIKE '%DROP TABLE%';
    ```

35. **Changements de permissions**  
    ```sql
    SELECT user, message 
    FROM logs WHERE tag = 'permission_change';
    ```

---

## **4. Requêtes d'Optimisation**  

### **Gestion des Données**  
36. **Logs à archiver (> 6 mois)**  
    ```sql
    SELECT COUNT(*) FROM logs 
    WHERE timestamp < DATE('now', '-6 months');
    ```

37. **Tags inutilisés**  
    ```sql
    SELECT tag, COUNT(*) as count 
    FROM logs GROUP BY tag 
    HAVING count < 5;
    ```

### **Performance des Requêtes**  
38. **Requêtes les plus lentes**  
    ```sql
    SELECT query, execution_time 
    FROM logs WHERE tag = 'slow_query' 
    ORDER BY execution_time DESC LIMIT 10;
    ```

39. **Index manquants**  
    ```sql
    SELECT json_extract(message, '$.table') as table, 
    json_extract(message, '$.query') as query 
    FROM logs WHERE tag = 'missing_index';
    ```

40. **Optimisation des jointures**  
    ```sql
    SELECT json_extract(message, '$.query') as query, 
    json_extract(message, '$.duration') as duration 
    FROM logs WHERE tag = 'query_optimization' 
    ORDER BY duration DESC LIMIT 5;
    ```

---

## **Recommandations pour le Client (Log Sender)**  
1. **Structurer les logs** en JSON pour faciliter l'extraction de champs.  
2. **Taguer systématiquement** les logs (`auth`, `checkout`, `api`).  
3. **Limiter les logs verbeux** (ex: stack traces sans contexte).  
4. **Envoyer par batches** pour réduire les appels HTTP.  

Exemple de log optimisé :  
```json
{
  "timestamp": "2025-06-12T14:30:00Z",
  "level": "ERROR",
  "tag": "payment_error",
  "message": {
    "error": "Timeout",
    "transaction_id": "tx_123",
    "amount": 150.00,
    "user_id": "usr_456"
  }
}
```

----------

## **Top 80 Requêtes SQL pour un Système de Logs (Suite)**  
*(Suite des 40 requêtes restantes, réparties en 4 catégories : Techniques, Métier, Sécurité, Optimisation)*  

---

## **3. Requêtes Sécurité (Suite)**  

### **Surveillance des Accès**  
41. **Connexions depuis de nouveaux pays**  
    ```sql
    SELECT country, COUNT(*) as connections 
    FROM logs 
    WHERE tag = 'geoip' 
    AND country NOT IN ('FR', 'DE', 'US')  -- Liste des pays habituels
    GROUP BY country;
    ```

42. **Activité en dehors des heures ouvrables**  
    ```sql
    SELECT user, COUNT(*) as after_hours_access
    FROM logs
    WHERE tag = 'auth_success'
    AND (strftime('%H', timestamp) < '08' OR strftime('%H', timestamp) > '18')
    GROUP BY user
    ORDER BY after_hours_access DESC;
    ```

43. **Utilisateurs avec multiples sessions concurrentes**  
    ```sql
    SELECT user, COUNT(DISTINCT session_id) as concurrent_sessions
    FROM logs
    WHERE tag = 'session_start'
    GROUP BY user
    HAVING concurrent_sessions > 3;
    ```

### **Détection d'Intrusions**  
44. **Scan de ports détecté**  
    ```sql
    SELECT host, COUNT(*) as port_scan_attempts
    FROM logs
    WHERE message LIKE '%port scan%' OR message LIKE '%nmap%'
    GROUP BY host;
    ```

45. **Tentatives d'injection SQL**  
    ```sql
    SELECT host, message
    FROM logs
    WHERE message LIKE '%1=1%' 
    OR message LIKE '%UNION SELECT%'
    OR message LIKE '%; DROP TABLE%';
    ```

46. **Utilisation d'outils de pentesting**  
    ```sql
    SELECT host, user_agent
    FROM logs
    WHERE user_agent LIKE '%sqlmap%'
    OR user_agent LIKE '%Burp Suite%'
    OR user_agent LIKE '%Metasploit%';
    ```

### **Audit des Permissions**  
47. **Changements de permissions critiques**  
    ```sql
    SELECT user, message, timestamp
    FROM logs
    WHERE tag = 'permission_change'
    AND message LIKE '%root%'
    ORDER BY timestamp DESC;
    ```

48. **Accès aux fichiers sensibles**  
    ```sql
    SELECT user, path
    FROM logs
    WHERE tag = 'file_access'
    AND path LIKE '%/etc/passwd%'
    OR path LIKE '%/.env%';
    ```

49. **Désactivation de logs suspecte**  
    ```sql
    SELECT user, timestamp
    FROM logs
    WHERE tag = 'config_change'
    AND message LIKE '%disable logging%';
    ```

### **Comportements Anormaux**  
50. **Uploads de fichiers volumineux**  
    ```sql
    SELECT user, json_extract(message, '$.file_size') as size
    FROM logs
    WHERE tag = 'file_upload'
    AND size > 1000000  -- 1 Mo
    ORDER BY size DESC;
    ```

51. **Téléchargements massifs**  
    ```sql
    SELECT user, COUNT(*) as downloads
    FROM logs
    WHERE tag = 'file_download'
    AND timestamp >= DATETIME('now', '-1 hour')
    GROUP BY user
    HAVING downloads > 50;
    ```

52. **Activité sur endpoints sensibles**  
    ```sql
    SELECT endpoint, COUNT(*) as hits
    FROM logs
    WHERE tag = 'api_request'
    AND endpoint IN ('/admin', '/backup', '/dbdump')
    GROUP BY endpoint;
    ```

53. **Requêtes DELETE inhabituelles**  
    ```sql
    SELECT user, COUNT(*) as deletes
    FROM logs
    WHERE tag = 'db_query'
    AND message LIKE '%DELETE FROM%'
    GROUP BY user
    HAVING deletes > 5;
    ```

54. **Modifications de configuration**  
    ```sql
    SELECT user, json_extract(message, '$.config_file') as file
    FROM logs
    WHERE tag = 'config_change'
    ORDER BY timestamp DESC
    LIMIT 20;
    ```

55. **Accès aux backups**  
    ```sql
    SELECT user, timestamp
    FROM logs
    WHERE tag = 'backup_access'
    ORDER BY timestamp DESC;
    ```

56. **Utilisation de comptes désactivés**  
    ```sql
    SELECT user, COUNT(*) as attempts
    FROM logs
    WHERE tag = 'auth_failed'
    AND message LIKE '%disabled account%'
    GROUP BY user;
    ```

57. **Activité sur les clés API**  
    ```sql
    SELECT api_key, COUNT(*) as uses
    FROM logs
    WHERE tag = 'api_auth'
    GROUP BY api_key
    ORDER BY uses DESC;
    ```

58. **Rotation des clés non respectée**  
    ```sql
    SELECT api_key, MAX(timestamp) as last_used
    FROM logs
    WHERE tag = 'api_auth'
    GROUP BY api_key
    HAVING last_used < DATE('now', '-90 days');
    ```

59. **Tentatives de désactivation du MFA**  
    ```sql
    SELECT user, timestamp
    FROM logs
    WHERE tag = 'mfa_change'
    AND message LIKE '%disable%';
    ```

60. **Modification des règles firewall**  
    ```sql
    SELECT user, message
    FROM logs
    WHERE tag = 'firewall_change'
    ORDER BY timestamp DESC;
    ```

---

## **4. Requêtes d'Optimisation (Suite)**  

### **Gestion des Données**  
61. **Logs dupliqués**  
    ```sql
    SELECT message, COUNT(*) as duplicates
    FROM logs
    GROUP BY message
    HAVING duplicates > 1
    ORDER BY duplicates DESC;
    ```

62. **Champs JSON inutilisés**  
    ```sql
    SELECT 
      json_extract(message, '$.unused_field') as unused_value,
      COUNT(*) as occurrences
    FROM logs
    WHERE json_extract(message, '$.unused_field') IS NOT NULL
    GROUP BY unused_value;
    ```

63. **Logs à faible valeur informative**  
    ```sql
    SELECT message, COUNT(*) as count
    FROM logs
    WHERE LENGTH(message) < 20
    GROUP BY message
    HAVING count > 100;
    ```

### **Performance des Requêtes**  
64. **Requêtes full table scan**  
    ```sql
    SELECT query, execution_time
    FROM logs
    WHERE tag = 'query_plan'
    AND message LIKE '%SCAN TABLE%'
    ORDER BY execution_time DESC;
    ```

65. **Requêtes sans index utilisés**  
    ```sql
    SELECT query
    FROM logs
    WHERE tag = 'query_plan'
    AND message LIKE '%USING INDEX%' = 0;
    ```

66. **Top 10 des requêtes les plus coûteuses**  
    ```sql
    SELECT query, SUM(execution_time) as total_time
    FROM logs
    WHERE tag = 'query_perf'
    GROUP BY query
    ORDER BY total_time DESC
    LIMIT 10;
    ```

### **Optimisation du Stockage**  
67. **Logs à archiver (> 1 an)**  
    ```sql
    SELECT COUNT(*) as old_logs
    FROM logs
    WHERE timestamp < DATE('now', '-1 year');
    ```

68. **Taux de compression par type de log**  
    ```sql
    SELECT tag, 
      AVG(LENGTH(message)) as avg_size,
      AVG(LENGTH(COMPRESS(message))) as avg_compressed
    FROM logs
    GROUP BY tag;
    ```

69. **Tags consommant le plus d'espace**  
    ```sql
    SELECT tag, SUM(LENGTH(message)) as total_bytes
    FROM logs
    GROUP BY tag
    ORDER BY total_bytes DESC;
    ```

70. **Optimisation des types de données**  
    ```sql
    SELECT 
      typeof(json_extract(message, '$.numeric_field')) as data_type,
      COUNT(*) as occurrences
    FROM logs
    WHERE json_extract(message, '$.numeric_field') IS NOT NULL
    GROUP BY data_type;
    ```

### **Maintenance**  
71. **Tâches de maintenance longues**  
    ```sql
    SELECT task, duration
    FROM logs
    WHERE tag = 'maintenance'
    AND duration > 3600  -- 1 heure
    ORDER BY duration DESC;
    ```

72. **Échecs de backup**  
    ```sql
    SELECT timestamp, message
    FROM logs
    WHERE tag = 'backup'
    AND level = 'ERROR'
    ORDER BY timestamp DESC;
    ```

73. **Synchronisations de bases échouées**  
    ```sql
    SELECT timestamp, message
    FROM logs
    WHERE tag = 'db_sync'
    AND level = 'ERROR';
    ```

74. **Mises à jour critiques manquantes**  
    ```sql
    SELECT component, MAX(version) as latest_version
    FROM logs
    WHERE tag = 'version_check'
    GROUP BY component
    HAVING latest_version < '2.0.0';  -- Version minimale requise
    ```

75. **Jobs planifiés non exécutés**  
    ```sql
    SELECT job_name, COUNT(*) as missed_runs
    FROM logs
    WHERE tag = 'scheduled_job'
    AND message LIKE '%missed%'
    GROUP BY job_name;
    ```

### **Analyse des Schémas**  
76. **Champs JSON les plus utilisés**  
    ```sql
    SELECT 
      json_extract(message, '$.field') as field_name,
      COUNT(*) as occurrences
    FROM logs
    WHERE json_extract(message, '$.field') IS NOT NULL
    GROUP BY field_name
    ORDER BY occurrences DESC
    LIMIT 10;
    ```

77. **Évolution des schémas de logs**  
    ```sql
    SELECT 
      DATE(timestamp) as day,
      json_group_array(DISTINCT json_extract(message, '$.field')) as fields
    FROM logs
    GROUP BY day
    ORDER BY day DESC;
    ```

78. **Compatibilité des schémas**  
    ```sql
    SELECT 
      application,
      COUNT(DISTINCT json_extract(message, '$.version')) as schema_versions
    FROM logs
    GROUP BY application
    HAVING schema_versions > 1;
    ```

79. **Champs obligatoires manquants**  
    ```sql
    SELECT COUNT(*) as missing_required
    FROM logs
    WHERE json_extract(message, '$.required_field') IS NULL;
    ```

80. **Migration des anciens formats**  
    ```sql
    SELECT COUNT(*) as legacy_logs
    FROM logs
    WHERE message NOT LIKE '%{%';  -- Logs non-JSON
    ```

---

## **Recommandations Complémentaires pour le Log Sender**  

### **Stratégie d'Envoi Optimisée**  
1. **Priorisation des logs critiques**  
   - Envoyer en temps réel : `ERROR`, `security`, `transaction`  
   - Envoyer par batch : `INFO`, `DEBUG`  

2. **Compression des payloads**  
   ```python
   import zlib
   compressed_log = zlib.compress(json.dumps(log_entry).encode())
   ```

3. **Gestion des erreurs réseau**  
   ```python
   def send_log(log):
       try:
           requests.post(server_url, json=log, timeout=5)
       except Exception as e:
           write_to_fallback_file(log)  # Mécanisme de reprise
   ```

### **Exemple de Log Métier Idéal**  
```json
{
  "timestamp": "2025-06-12T14:30:00Z",
  "level": "ERROR",
  "tag": "payment_failed",
  "application": "checkout",
  "user_id": "usr_789",
  "session_id": "sess_xyz",
  "metrics": {
    "transaction_amount": 150.00,
    "payment_gateway": "stripe",
    "error_code": "gateway_timeout"
  },
  "context": {
    "device": "mobile",
    "ip": "192.168.1.100",
    "country": "FR"
  }
}
```

### **Checklist de Validation**  
- [ ] Tous les logs ont un `tag` valide  
- [ ] Les champs métiers sont normalisés (`user_id` au lieu de `user`)  
- [ ] Les erreurs incluent un `error_code` standardisé  
- [ ] La taille moyenne des logs est < 1 Ko  

--- 

Ce catalogue complet permet d'exploiter pleinement votre système de logs, depuis le monitoring technique jusqu'à l'analyse métier avancée, tout en garantissant sécurité et performance.
