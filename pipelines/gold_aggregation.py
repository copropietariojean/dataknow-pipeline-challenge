import os
import subprocess
import pandas as pd
import numpy as np
from datetime import datetime
from azure.storage.blob import BlobServiceClient

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
silver_dir = os.path.join(base_dir, "pipelines", "data", "silver")
gold_dir = os.path.join(base_dir, "pipelines", "data", "gold")
os.makedirs(gold_dir, exist_ok=True)

cmd = 'az storage account show-connection-string --name stfinbankdevrch7 --resource-group rg-finbank-dev --query connectionString -o tsv'
conn_str = subprocess.check_output(cmd, shell=True).decode().strip()
blob_service_client = BlobServiceClient.from_connection_string(conn_str)
gold_container_client = blob_service_client.get_container_client("gold")

print("="*60)
print(">>> INICIANDO PROCESAMIENTO CAPA GOLD (MODELO DIMENSIONAL Y KPIS)")
print("="*60)

# Cargar data limpia de Silver
df_cli = pd.read_parquet(os.path.join(silver_dir, "TB_CLIENTES_CORE_silver.parquet"))
df_prod = pd.read_parquet(os.path.join(silver_dir, "TB_PRODUCTOS_CAT_silver.parquet"))
df_suc = pd.read_parquet(os.path.join(silver_dir, "TB_SUCURSALES_RED_silver.parquet"))
df_ob = pd.read_parquet(os.path.join(silver_dir, "TB_OBLIGACIONES_silver.parquet"))
df_mov = pd.read_parquet(os.path.join(silver_dir, "TB_MOV_FINANCIEROS_silver.parquet"))
df_com = pd.read_parquet(os.path.join(silver_dir, "TB_COMISIONES_LOG_silver.parquet"))

# 1. DIM_CLIENTES: Edad y Mapeo
hoy = datetime.now()
df_cli["fec_nac_dt"] = pd.to_datetime(df_cli["fec_nac"], errors="coerce")
df_cli["edad"] = hoy.year - df_cli["fec_nac_dt"].dt.year
dim_clientes = df_cli[["id_cli", "nombre_completo", "tip_doc", "num_doc_hash", "edad", "cod_segmento", "score_buro", "ciudad_res", "estado_cli"]].copy()

# 2. DIM_PRODUCTOS: Tasa mensual equivalente y Familia
df_prod["tasa_mes_equiv"] = ((1 + df_prod["tasa_ea"]) ** (1/12) - 1).round(4)
df_prod["familia_producto"] = np.where(df_prod["tip_prod"].str.contains("Crédito|Tarjeta"), "Crédito", 
                              np.where(df_prod["tip_prod"].str.contains("Ahorro"), "Ahorro", "Transaccional"))
dim_productos = df_prod[["cod_prod", "desc_prod", "tip_prod", "familia_producto", "tasa_ea", "tasa_mes_equiv", "comision_admin", "estado_prod"]].copy()

# 3. DIM_GEOGRAFIA y DIM_CANAL
dim_geografia = df_suc[["ciudad", "depto", "latitud", "longitud"]].drop_duplicates().reset_index(drop=True)
dim_geografia["id_geo"] = dim_geografia.index + 1

dim_canal = df_suc[["cod_suc", "nom_suc", "tip_punto", "activo"]].copy()

# 4. FACT_CARTERA: Regla de Negocio de Buckets de Mora y Provisiones (Página 6)
def clasificar_mora(dias):
    if dias == 0: return "Al día"
    elif dias <= 30: return "Rango 1 (1-30 días)"
    elif dias <= 60: return "Rango 2 (31-60 días)"
    elif dias <= 90: return "Rango 3 (61-90 días)"
    else: return "Deteriorado (>90 días)"

df_ob["bucket_mora"] = df_ob["dias_mora_act"].apply(clasificar_mora)
# Provisión regulatoria estimada según norma financiera
prov_map = {"Al día": 0.01, "Rango 1 (1-30 días)": 0.05, "Rango 2 (31-60 días)": 0.20, "Rango 3 (61-90 días)": 0.50, "Deteriorado (>90 días)": 1.00}
df_ob["porc_provision"] = df_ob["bucket_mora"].map(prov_map)
df_ob["provision_estimada"] = (df_ob["sdo_capital"] * df_ob["porc_provision"]).round(2)
fact_cartera = df_ob.copy()

# 5. FACT_TRANSACCIONES: Conversión a USD y Flag de Horario Hábil
TRM_COP_USD = 4200.0  # Tasa representativa para conversión
df_mov["monto_usd"] = (df_mov["vr_mov"] / TRM_COP_USD).round(2)
df_mov["hora_num"] = pd.to_datetime(df_mov["hra_mov"], format="%H:%M:%S").dt.hour
df_mov["es_horario_habil"] = np.where((df_mov["hora_num"] >= 8) & (df_mov["hora_num"] <= 18), 1, 0)
fact_transacciones = df_mov.copy()

# 6. TABLA EJECUTIVA GOLD: KPIs Diarios de Cartera (Página 6)
kpi_cartera = fact_cartera.merge(dim_clientes[["id_cli", "cod_segmento", "ciudad_res"]], on="id_cli", how="left")
kpi_diarios_cartera = kpi_cartera.groupby(["fec_desembolso", "cod_prod", "cod_segmento", "ciudad_res"]).agg(
    total_obligaciones=("id_oblig", "count"),
    saldo_total_cartera=("sdo_capital", "sum"),
    saldo_en_mora=("sdo_capital", lambda x: x[kpi_cartera.loc[x.index, "dias_mora_act"] > 0].sum()),
    provision_total=("provision_estimada", "sum"),
    clientes_en_mora=("id_cli", lambda x: x[kpi_cartera.loc[x.index, "dias_mora_act"] > 0].nunique())
).reset_index()

kpi_diarios_cartera["tasa_mora_porc"] = ((kpi_diarios_cartera["saldo_en_mora"] / kpi_diarios_cartera["saldo_total_cartera"]) * 100).round(2)

# 7. FACT_RENTABILIDAD_CLIENTE: Cálculo de CLTV y Comisiones Mensuales (Página 6)
df_com["periodo_mes"] = pd.to_datetime(df_com["fec_cobro"]).dt.to_period("M").astype(str)
com_cliente = df_com.groupby(["id_cli", "periodo_mes"])["vr_comision"].sum().reset_index()

# Estimación de ingresos por intereses desde obligaciones
int_cliente = fact_cartera.groupby("id_cli")["vr_cuota"].sum().reset_index().rename(columns={"vr_cuota": "ingreso_intereses"})

fact_rentabilidad_cliente = com_cliente.merge(int_cliente, on="id_cli", how="left").fillna(0)
fact_rentabilidad_cliente["ingreso_total"] = fact_rentabilidad_cliente["vr_comision"] + (fact_rentabilidad_cliente["ingreso_intereses"] * 0.15)
# CLTV Acumulado
fact_rentabilidad_cliente["cltv_acumulado"] = fact_rentabilidad_cliente.groupby("id_cli")["ingreso_total"].cumsum().round(2)

# Guardar y subir toda la Capa Gold a Azure
tablas_gold = {
    "dim_clientes": dim_clientes,
    "dim_productos": dim_productos,
    "dim_geografia": dim_geografia,
    "dim_canal": dim_canal,
    "fact_cartera": fact_cartera,
    "fact_transacciones": fact_transacciones,
    "kpi_diarios_cartera": kpi_diarios_cartera,
    "fact_rentabilidad_cliente": fact_rentabilidad_cliente
}

for name, df_g in tablas_gold.items():
    loc_f = os.path.join(gold_dir, f"{name}.parquet")
    df_g.to_parquet(loc_f, index=False)
    gold_container_client.get_blob_client(f"{name}/{name}.parquet").upload_blob(open(loc_f, "rb"), overwrite=True)
    print(f"✔ {name.ljust(22)} | {len(df_g):,} registros generados y sincronizados con Azure Gold")

print("="*60)
print(">>> MODELO DIMENSIONAL GOLD Y TABLA EJECUTIVA DESPLEGADOS EN AZURE")
print("="*60)