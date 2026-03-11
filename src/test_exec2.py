from Utils.SQLUtils import execute_sql_query

query = """
EXEC usp_VtasGerencia N'SAL', 1, '', '', '', '', '', '', '2026-01-01', '2026-01-31'
"""
print("Result with 2026-01-01 format:")
print(execute_sql_query(query))
