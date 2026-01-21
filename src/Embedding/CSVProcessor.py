import csv
from collections import defaultdict
from pathlib import Path

# ---------- CONFIG ----------
SCHEMA_CSV = "../DBBSchemas/Tables.csv"
PK_CSV = "../DBBSchemas/ForeingKeys.csv"
OUTPUT_DIR = "../DBBSchemas/Embeddings"
DB_DIALECT = "SQL Server (T-SQL)"
# ----------------------------

Path(OUTPUT_DIR).mkdir(exist_ok=True)

tables = defaultdict(list)
primary_keys = defaultdict(set)

# Leer PKs
with open(PK_CSV, newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        key = f"{row['Table_Schema']}.{row['Table_NamE']}"
        primary_keys[key].add(row["Column_Name"])

# Leer columnas
with open(SCHEMA_CSV, newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        table_key = f"{row['TABLE_SCHEMA']}.{row['TABLE_NAME']}"
        column = row["COLUMN_NAME"]
        data_type = row["DATA_TYPE"].upper()
        nullable = "NULL" if row["IS_NULLABLE"] == "YES" else "NOT NULL"

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
