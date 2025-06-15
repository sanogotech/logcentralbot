def get_db_handler(db_type='sqlite'):
    """
    Factory pour créer des instances de gestionnaires de base de données
    
    Args:
        db_type (str): Type de base de données ('sqlite', 'mysql', 'mongodb')
    
    Returns:
        Instance du gestionnaire de base de données approprié
    
    Raises:
        ValueError: Si le type de base de données n'est pas supporté
        ImportError: Si le module requis n'est pas disponible
    """
    try:
        if db_type == 'sqlite':
            from db_sqlite import SQLiteHandler
            return SQLiteHandler()
        elif db_type == 'mysql':
            from db_mysql import MySQLHandler
            return MySQLHandler()
        elif db_type == 'mongodb':
            from db_mongodb import MongoDBHandler
            return MongoDBHandler()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    except ImportError as e:
        raise ImportError(f"Failed to import database handler for {db_type}: {str(e)}")