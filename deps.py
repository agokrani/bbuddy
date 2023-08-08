import psycopg

connection_string = "postgresql://bijmbrqw:xnnbF7f-i_X-9uPRnUreaOOJFS-d9oWt@dumbo.db.elephantsql.com/bijmbrqw"

#def get_db(): 
#    connection = psycopg.connect(connection_string)
#
#    connection.autocommit = False
#
#    try:
#        yield connection
#    finally:
#        connection.close()
#

_singleton_connection = None

def get_db():
    global _singleton_connection

    if _singleton_connection is None:
        _singleton_connection = psycopg.connect(connection_string)
        _singleton_connection.autocommit = False

    try:
        yield _singleton_connection
    finally:
        # You can choose to keep the connection open or close it upon generator exhaustion
        pass
