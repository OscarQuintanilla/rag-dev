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
    print(f"\n--- [SQLUtils] Executing Query ---\n{query}\n----------------------------------")
    try:
        # We must use SET NOCOUNT ON to prevent pyodbc from getting stuck on empty "rows affected" messages
        # SSMS default settings that might be required by complex views or indexes inside the SP
        # Added DATEFORMAT, LANGUAGE, and FMTONLY OFF to accommodate pyodbc quirks with temp tables
        query = f"SET DATEFORMAT dmy;\nSET LANGUAGE Spanish;\nSET ARITHABORT ON;\nSET ANSI_NULLS ON;\nSET ANSI_WARNINGS ON;\nSET NOCOUNT ON;\nSET FMTONLY OFF;\n{query}"
        
        connection_string = get_db_connection_string()
        engine = create_engine(connection_string)
        
        # Use raw DBI connection to get access to the underlying cursor and nextset()
        # raw_connection() doesn't support the 'with' context manager in SQLAlchemy
        raw_conn = engine.raw_connection()
        # Many stored procedures require autocommit (no implicit transactions) to work properly in pyodbc
        raw_conn.autocommit = True
        try:
            print("[SQLUtils] Connection established. Executing...")
            cursor = raw_conn.cursor()
            cursor.execute(query)
            print("[SQLUtils] Query execution successful.")
            print(cursor)
            
            all_result_sets = []
            set_index = 1
            
            # Fix this since it doesnt return multiple result sets
            
            while True:
                if cursor.description is not None:
                    # found a result set
                    keys = [column[0] for column in cursor.description]
                    rows = cursor.fetchall()
                    print(f"\n[SQLUtils] --- RESULT SET #{set_index} ---")
                    print(f"Columns: {keys}")
                    print(f"Row count: {len(rows)}")
                    if len(rows) > 0:
                        print(f"First row: {rows[0]}")
                    
                    data = [dict(zip(keys, row)) for row in rows]
                    all_result_sets.append({
                        "set_index": set_index,
                        "data": data,
                        "row_count": len(rows)
                    })
                    set_index += 1
                else:
                    print(f"\n[SQLUtils] --- RESULT SET #{set_index} --- No Columns (Empty Result/Message)")
                    set_index += 1
                    
                # Check for the next result set
                if not cursor.nextset():
                    break
            
            print(f"\n[SQLUtils] Total result sets found: {len(all_result_sets)}")
            
            # Find the first result set that actually has data
            for rs in all_result_sets:
                if rs["row_count"] > 0:
                    print(f"[SQLUtils] Returning Result Set #{rs['set_index']} which has {rs['row_count']} rows.")
                    return rs["data"]
            
            # If we get here, no result set had data.
            print("[SQLUtils] None of the result sets had data. Returning empty list.")
            return []
        finally:
            raw_conn.close()
    except Exception as e:
        print(f"\n[SQLUtils] ERROR executing SQL: {e}\n")
        return {"error": str(e)}
