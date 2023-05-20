import psycopg

connection_string = "postgresql://bijmbrqw:xnnbF7f-i_X-9uPRnUreaOOJFS-d9oWt@dumbo.db.elephantsql.com/bijmbrqw"

def get_db(): 
    connection = psycopg.connect(connection_string)

    connection.autocommit = False

    try:
        yield connection
    finally:
        connection.close()

