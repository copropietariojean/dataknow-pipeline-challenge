import os
import sqlite3
import pandas as pd

base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, "data")
db_path = os.path.join(base_dir, "finbank_source.db")
schema_path = os.path.join(base_dir, "schema.sql")

# 1. Conexión y creación de tablas con schema.sql
conn = sqlite3.connect(db_path)
with open(schema_path, "r", encoding="utf-8") as f:
    conn.executescript(f.read())
print(">>> Tablas creadas exitosamente en la base de datos SQL.")

# 2. Carga desde los diferentes formatos generados
print(">>> Cargando TB_PRODUCTOS_CAT (desde JSON)...")
df_prod = pd.read_json(os.path.join(data_dir, "TB_PRODUCTOS_CAT.json"))
df_prod.to_sql("TB_PRODUCTOS_CAT", conn, if_exists="replace", index=False)

print(">>> Cargando TB_SUCURSALES_RED (desde CSV)...")
df_suc = pd.read_csv(os.path.join(data_dir, "TB_SUCURSALES_RED.csv"))
df_suc.to_sql("TB_SUCURSALES_RED", conn, if_exists="replace", index=False)

print(">>> Cargando TB_CLIENTES_CORE (desde CSV)...")
df_cli = pd.read_csv(os.path.join(data_dir, "TB_CLIENTES_CORE.csv"))
df_cli.to_sql("TB_CLIENTES_CORE", conn, if_exists="replace", index=False)

print(">>> Cargando TB_OBLIGACIONES (desde Parquet)...")
df_ob = pd.read_parquet(os.path.join(data_dir, "TB_OBLIGACIONES.parquet"))
df_ob.to_sql("TB_OBLIGACIONES", conn, if_exists="replace", index=False)

print(">>> Cargando TB_MOV_FINANCIEROS (desde Parquet)...")
df_mov = pd.read_parquet(os.path.join(data_dir, "TB_MOV_FINANCIEROS.parquet"))
df_mov.to_sql("TB_MOV_FINANCIEROS", conn, if_exists="replace", index=False)

print(">>> Cargando TB_COMISIONES_LOG (desde Parquet)...")
df_com = pd.read_parquet(os.path.join(data_dir, "TB_COMISIONES_LOG.parquet"))
df_com.to_sql("TB_COMISIONES_LOG", conn, if_exists="replace", index=False)

# 3. Validación y Evidencia de Carga: SELECT COUNT(*)
print("\n" + "="*50)
print("EVIDENCIA DE CARGA EXITOSA (SELECT COUNT(*)):")
print("="*50)
cursor = conn.cursor()
tables = ["TB_CLIENTES_CORE", "TB_PRODUCTOS_CAT", "TB_SUCURSALES_RED", 
          "TB_OBLIGACIONES", "TB_MOV_FINANCIEROS", "TB_COMISIONES_LOG"]

for t in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {t}")
    count = cursor.fetchone()[0]
    print(f"Tabla: {t.ljust(25)} | Total Registros: {count:,}")

conn.close()
print("="*50)
print(">>> Carga a Base de Datos Relacional completada con éxito.")