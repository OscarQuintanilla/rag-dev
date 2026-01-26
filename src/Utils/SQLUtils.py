import os
import urllib
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def get_db_connection_string():
    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_DATABASE")
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    driver = '{ODBC Driver 17 for SQL Server}'
    
    # Construct connection string
    params = urllib.parse.quote_plus(
        f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    )
    return f"mssql+pyodbc:///?odbc_connect={params}"

def execute_sql_query(query: str):
    try:
        connection_string = get_db_connection_string()
        engine = create_engine(connection_string)
        
        with engine.connect() as connection:
            result = connection.execute(text(query))
            # Get column names
            keys = result.keys()
            # Fetch all rows and convert to dict
            data = [dict(zip(keys, row)) for row in result.fetchall()]
            return data
    except Exception as e:
        print(f"Error executing SQL: {e}")
        return {"error": str(e)}
