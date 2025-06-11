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
        raise ValueError(f"Unsupported database type: {dbtype}")

