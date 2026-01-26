from ..Utils.SQLUtils import execute_sql_query

def execute_sql_from_request(query: str):
    return execute_sql_query(query)
