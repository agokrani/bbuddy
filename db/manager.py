import psycopg


class DatabaseManager:
    _connection = None
    connection_string = "postgresql://bijmbrqw:xnnbF7f-i_X-9uPRnUreaOOJFS-d9oWt@dumbo.db.elephantsql.com/bijmbrqw"

    @classmethod
    def get_connection(cls):
        if cls._connection is None or cls._connection.closed != 0:
            cls._connection = cls._create_connection()
        return cls._connection

    @classmethod
    def _create_connection(cls):
        conn = psycopg.connect(cls.connection_string)
        return conn