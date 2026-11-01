import os
import hashlib
import subprocess
import pandas as pd
import numpy as np
from datetime import datetime
from azure.storage.blob import BlobServiceClient

# 1. Configuración de Directorios y Conexión
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bronze_dir = os.path.join(base_dir, "pipelines", "data", "bronze")
silver_dir = os.path.join(base_dir, "pipelines", "data", "silver")
os.makedirs(silver_dir, exist_ok=True)

cmd = 'az storage account show-connection-string --name stfinbankdevrch7 --resource-group rg-finbank-dev --query connectionString -o tsv'
conn_str = subprocess.check_output(cmd, shell=True).decode().strip()
blob_service_client = BlobServiceClient.from_connection_string(conn_str)
silver_container_client = blob_service_client.get_container_client("silver")

print("="*60)
print(">>> INICIANDO PROCESAMIENTO CAPA SILVER (LIMPIEZA Y SEGURIDAD)")
print("="*60)

# Función de Encriptación HASH SHA-256 para Cédulas (Protección de Datos)
def hash_sensible(valor):
    return hashlib.sha256(str(valor).encode('utf-8')).hexdigest()[:16]

# --- 1. PROCESAR CLIENTES ---
# Buscar el archivo parquet de clientes dentro de las particiones
cli_path = None
for root, dirs, files in os.walk(os.path.join(bronze_dir, "TB_CLIENTES_CORE")):
    for f in files:
        if f.endswith(".parquet"):
            cli_path = os.path.join(root, f)

df_cli = pd.read_parquet(cli_path)
n_original_cli = len(df_cli)
# Enmascarar documento con Hash criptográfico
df_cli["num_doc_hash"] = df_cli["num_doc"].apply(hash_sensible)
df_cli.drop(columns=["num_doc"], inplace=True)
# Imputación de nulos controlados en ciudad
df_cli["ciudad_res"] = df_cli["ciudad_res"].fillna("NO REPORTADA")
df_cli["depto_res"] = df_cli["depto_res"].fillna("NO REPORTADO")
# Estandarizar nombre completo
df_cli["nombre_completo"] = df_cli["nomb_cli"].str.strip() + " " + df_cli["apell_cli"].str.strip()

# --- 2. PROCESAR TRANSACCIONES (MOVIMIENTOS) ---
mov_path = None
for root, dirs, files in os.walk(os.path.join(bronze_dir, "TB_MOV_FINANCIEROS")):
    for f in files:
        if f.endswith(".parquet"):
            mov_path = os.path.join(root, f)

df_mov = pd.read_parquet(mov_path)
n_original_mov = len(df_mov)

# Detección y Separación a TABLA DE ERRORES (Montos negativos y fechas anómalas)
filtro_errores = (df_mov["vr_mov"] <= 0) | (df_mov["fec_mov"] > "2028-01-01")
df_errores = df_mov[filtro_errores].copy()
df_errores["motivo_error"] = np.where(df_errores["vr_mov"] <= 0, "MONTO_INVALIDO_NEGATIVO", "FECHA_ANOMALA_FUTURA")
df_errores["fecha_deteccion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Filtrar data limpia
df_mov_clean = df_mov[~filtro_errores].copy()

# Deduplicación: Eliminar los 10 duplicados exactos inyectados
df_mov_clean.drop_duplicates(subset=["id_mov"], keep="first", inplace=True)

# Lógica de Fraude en Silver: Detección de transacción atípica (> 3 desviaciones estándar)
media_mov = df_mov_clean["vr_mov"].mean()
std_mov = df_mov_clean["vr_mov"].std()
umbral_atipico = media_mov + (3 * std_mov)
df_mov_clean["ind_sospechoso"] = np.where(df_mov_clean["vr_mov"] > umbral_atipico, 1, 0)

# --- 3. PROCESAR OBLIGACIONES Y PRODUCTOS ---
for t in ["TB_PRODUCTOS_CAT", "TB_SUCURSALES_RED", "TB_OBLIGACIONES", "TB_COMISIONES_LOG"]:
    for root, dirs, files in os.walk(os.path.join(bronze_dir, t)):
        for f in files:
            if f.endswith(".parquet"):
                df_temp = pd.read_parquet(os.path.join(root, f))
                loc_f = os.path.join(silver_dir, f"{t}_silver.parquet")
                df_temp.to_parquet(loc_f, index=False)
                # Subir a Azure Silver
                silver_container_client.get_blob_client(f"{t}/{t}_silver.parquet").upload_blob(open(loc_f, "rb"), overwrite=True)

# Guardar y subir Clientes, Movimientos y Errores
dfs_silver = {
    "TB_CLIENTES_CORE": df_cli,
    "TB_MOV_FINANCIEROS": df_mov_clean,
    "TB_ERRORES_PIPELINE": df_errores
}

for name, df_s in dfs_silver.items():
    loc_f = os.path.join(silver_dir, f"{name}_silver.parquet")
    df_s.to_parquet(loc_f, index=False)
    silver_container_client.get_blob_client(f"{name}/{name}_silver.parquet").upload_blob(open(loc_f, "rb"), overwrite=True)

print("="*60)
print(f"✔ CLIENTES SILVER        | {len(df_cli):,} filas | Cédulas Hasheadas con SHA-256")
print(f"✔ MOVIMIENTOS SILVER     | {len(df_mov_clean):,} filas limpias | Duplicados eliminados")
print(f"✔ TABLA DE ERRORES       | {len(df_errores):,} anomalías aisladas con éxito")
print(f"✔ ALERTAS DE FRAUDE      | {df_mov_clean['ind_sospechoso'].sum():,} transacciones sospechosas marcadas")
print("="*60)
print(">>> CAPA SILVER COMPLETADA Y SINCRONIZADA CON AZURE DATA LAKE")
print("="*60)