import os
import uuid
import sqlite3
import pandas as pd
from datetime import datetime
from azure.identity import AzureCliCredential
from azure.storage.blob import BlobServiceClient

# 1. Configuración de Rutas y Conexión
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, "data-generation", "finbank_source.db")
output_bronze_dir = os.path.join(base_dir, "pipelines", "data", "bronze")
os.makedirs(output_bronze_dir, exist_ok=True)

# Parámetros del Data Lake desplegado en la Fase 2
STORAGE_ACCOUNT_NAME = "stfinbankdevrch7"  # Tu storage account de Terraform
ACCOUNT_URL = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net"

import subprocess

# Obtener conexión autorizada de Azure de forma dinámica (sin quemar claves en código)
cmd = 'az storage account show-connection-string --name stfinbankdevrch7 --resource-group rg-finbank-dev --query connectionString -o tsv'
conn_str = subprocess.check_output(cmd, shell=True).decode().strip()
blob_service_client = BlobServiceClient.from_connection_string(conn_str)
bronze_container_client = blob_service_client.get_container_client("bronze")

# 3. Metadatos de Auditoría Mandatorios
id_lote = str(uuid.uuid4())
fecha_ingesta = datetime.now()
particion_ruta = f"year={fecha_ingesta.strftime('%Y')}/month={fecha_ingesta.strftime('%m')}/day={fecha_ingesta.strftime('%d')}"

tablas = [
    "TB_CLIENTES_CORE", "TB_PRODUCTOS_CAT", "TB_SUCURSALES_RED",
    "TB_OBLIGACIONES", "TB_MOV_FINANCIEROS", "TB_COMISIONES_LOG"
]

print("="*60)
print(f">>> INICIANDO INGESTA CAPA BRONZE | Lote: {id_lote}")
print(f">>> Particionamiento: {particion_ruta}")
print("="*60)

conn = sqlite3.connect(db_path)

for tabla in tablas:
    inicio = datetime.now()
    # Extracción cruda desde SQL
    df = pd.read_sql_query(f"SELECT * FROM {tabla}", conn)
    
    # Enriquecimiento con Metadatos de Auditoría
    df["fecha_ingesta"] = fecha_ingesta.strftime("%Y-%m-%d %H:%M:%S")
    df["sistema_fuente"] = "FINBANK_CORE_SQL"
    df["id_lote"] = id_lote
    
    # Guardar localmente en formato Parquet
    local_folder = os.path.join(output_bronze_dir, tabla, particion_ruta)
    os.makedirs(local_folder, exist_ok=True)
    local_file = os.path.join(local_folder, f"{tabla}.parquet")
    df.to_parquet(local_file, index=False)
    
    # Subir a Azure Data Lake (Contenedor Bronze)
    blob_remote_path = f"{tabla}/{particion_ruta}/{tabla}.parquet"
    blob_client = bronze_container_client.get_blob_client(blob_remote_path)
    with open(local_file, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
        
    duracion = (datetime.now() - inicio).total_seconds()
    peso_mb = os.path.getsize(local_file) / (1024 * 1024)
    print(f"✔ {tabla.ljust(22)} | {len(df):,} filas | {peso_mb:.2f} MB | {duracion:.2f}s -> Azure Bronze")

conn.close()
print("="*60)
print(">>> INGESTA BRONZE COMPLETADA EXITOSAMENTE EN AZURE DATA LAKE")
print("="*60)