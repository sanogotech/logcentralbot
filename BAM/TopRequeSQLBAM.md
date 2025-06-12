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
