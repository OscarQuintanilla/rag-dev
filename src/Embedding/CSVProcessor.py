import csv
from collections import defaultdict
from pathlib import Path

# # ---------- CONFIG ----------
# SCHEMA_CSV = "../DBBSchemas/Tables.csv"
# PK_CSV = "../DBBSchemas/ForeingKeys.csv"
# OUTPUT_DIR = "../DBBSchemas/Embeddings"
# DB_DIALECT = "SQL Server (T-SQL)"
# # ----------------------------
# ---------- CONFIG FOR NAHOMIS BOUTIQUE----------
SCHEMA_CSV = "../DBBSchemas/NahomisBoutique.csv"
PK_CSV = "../DBBSchemas/NahomisBoutique_FK.csv"
OUTPUT_DIR = "../DBBSchemas/Embeddings"
DB_DIALECT = "SQL Server (T-SQL)"
# ----------------------------

Path(OUTPUT_DIR).mkdir(exist_ok=True)

tables = defaultdict(list)
primary_keys = defaultdict(set)

# Leer PKs
with open(PK_CSV, newline="", encoding="utf-8-sig") as f:
    # Read first line to detect if it has headers like 'Table_Schema' or just data
    first_line = f.readline()
    f.seek(0)
    
    # Use semicolon delimiter if we detect it, else comma
    delimiter = ';' if ';' in first_line else ','
    
    if "Table_Schema" in first_line or "Table_NamE" in first_line:
        reader = csv.DictReader(f, delimiter=delimiter)
        for row in reader:
            schema = row.get('Table_Schema', 'dbo')
            table = row.get('Table_NamE', row.get('TABLE_NAME', ''))
            key = f"{schema}.{table}"
            primary_keys[key].add(row.get("Column_Name", row.get("COLUMN_NAME", "")))
    else:
        # NahomisBoutique format is likely TableName;ColumnName
        reader = csv.reader(f, delimiter=delimiter)
        for row in reader:
            if len(row) >= 2:
                # We assume no schema in this format, or we default to 'dbo'
                # but to match how we will read the schema csv, we'll just use the table name
                # Actually, the original script used table_key without dbo for PKs if it matched
                table = row[0]
                column = row[1]
                key = f"dbo.{table}" # Defaulting to dbo to match the general pattern, or just table
                primary_keys[key].add(column)

# Leer columnas
with open(SCHEMA_CSV, newline="", encoding="utf-8-sig") as f:
    first_line = f.readline()
    f.seek(0)
    
    delimiter = ';' if ';' in first_line else ','
    
    if "TABLE_SCHEMA" in first_line or "TABLE_NAME" in first_line:
        reader = csv.DictReader(f, delimiter=delimiter)
        for row in reader:
            table_key = f"{row.get('TABLE_SCHEMA', 'dbo')}.{row['TABLE_NAME']}"
            column = row["COLUMN_NAME"]
            data_type = row["DATA_TYPE"].upper()
            nullable = "NULL" if row.get("IS_NULLABLE", "") == "YES" else "NOT NULL"

            pk_tag = " PK" if column in primary_keys.get(table_key, set()) else ""

            tables[table_key].append(
                f"- {column} {data_type}{pk_tag} {nullable}"
            )
    else:
        # NahomisBoutique format: TableName;ColumnName;DataType;IsNullable(0/1);Length
        reader = csv.reader(f, delimiter=delimiter)
        for row in reader:
            if len(row) >= 3:
                table_name = row[0]
                table_key = f"dbo.{table_name}" # Use dbo as default schema to match PK dict
                column = row[1]
                data_type = row[2].upper()
                nullable = "NULL" # Default or based on index 3 if available
                if len(row) > 3:
                    nullable = "NULL" if row[3] == "1" else "NOT NULL"

                pk_tag = " PK" if column in primary_keys.get(table_key, set()) else ""

                tables[table_key].append(
                    f"- {column} {data_type}{pk_tag} {nullable}"
                )

# Generar archivos por tabla
for table_name, columns in tables.items():
    # quitar el dbo. de table_name
    table_name = table_name.replace("dbo.", "")
    content = [
        f"ENTITY: {table_name} | DIALECT: {DB_DIALECT}",
        f"TABLE: {table_name}",
        "COLUMNS: " + ", ".join([c.replace("- ", "") for c in columns])
    ]

    output_file = Path(OUTPUT_DIR) / f"{table_name.replace('.', '_')}.txt"
    output_file.write_text("\n".join(content), encoding="utf-8")

print("✔️ Esquema + PK integrados correctamente")
