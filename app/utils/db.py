import mysql.connector

def database_connect():
    connection = mysql.connector.connect(host="localhost",
                                             port=3307,
                                             database="meetme",
                                             user="root",
                                             password="root")
    
    return connection

def execute_query(query, params=None, fetchone=False):
    connection = database_connect()
    cursor = connection.cursor()
    cursor.execute(query, params or ())

    # Determine if the query is a SELECT statement
    if query.strip().upper().startswith("SELECT"):
        if fetchone:
            result = cursor.fetchone()
        else:
            result = cursor.fetchall()
    else:
        # For INSERT, UPDATE, DELETE, return the number of affected rows
        connection.commit()  # Commit changes for these operations
        result = cursor.rowcount
    
    cursor.close()
    connection.close()
    return result