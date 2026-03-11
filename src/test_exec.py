import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Utils.SQLUtils import execute_sql_query

query = """
EXEC [dbo].[usp_VtasGerencia]
    @CodPais = N'SAL',
    @Dealer = 1,
    @Tda = '',
    @Cajero = '',
    @Vendedor = '',
    @Cliente = '',
    @Tipo = '',
    @FormaPago = '',
    @Desde = '01/01/2026',
    @Hasta = '31/01/2026';
"""

print("Executing query...")
result = execute_sql_query(query)
print("Result:", result)
