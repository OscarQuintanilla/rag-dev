import os
import urllib
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Explicitly load from the root .env
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../.env')))

def test_connection():
    try:
        server = os.getenv("DB_SERVER")
        database = os.getenv("DB_DATABASE")
        username = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        
        print(f"Server: {server}")
        print(f"Database: {database}")
        print(f"User: {username}")
        # print(f"Password: {password}") # Don't print password safely
        
        if not server or not database or not username:
             print("Missing environment variables!")
             return

        driver = '{ODBC Driver 17 for SQL Server}'
        
        params = urllib.parse.quote_plus(
            f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
        )
        connection_string = f"mssql+pyodbc:///?odbc_connect={params}"
        
        print("Attempting to connect...")
        engine = create_engine(connection_string)
        
        with engine.connect() as connection:
            print("Connected successfully!")
            result = connection.execute(text("SELECT COUNT(*) as count FROM Dealer"))
            row = result.fetchone()
            print(f"Query Result: {row}")
            
    except Exception as e:
        print(f"Conection Failed: {e}")

if __name__ == "__main__":
    test_connection()
