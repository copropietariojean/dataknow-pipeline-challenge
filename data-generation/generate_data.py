import os
import json
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from faker import Faker

# 1. CARGA DE CONFIGURACIÓN Y FIJACIÓN DE SEMILLA (REPRODUCIBILIDAD)
base_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_dir, "config.json")
with open(config_path, "r") as f:
    config = json.load(f)

SEED = config["seed"]
random.seed(SEED)
np.random.seed(SEED)
fake = Faker("es_CO")
Faker.seed(SEED)

vols = config["volumes"]
start_dt = datetime.strptime(config["date_range"]["start_date"], "%Y-%m-%d")
end_dt = datetime.strptime(config["date_range"]["end_date"], "%Y-%m-%d")
days_range = (end_dt - start_dt).days

out_dir = os.path.join(base_dir, "data")
os.makedirs(out_dir, exist_ok=True)

print(">>> [1/6] Generando TB_PRODUCTOS_CAT...")
tipos = ["Crédito de Consumo", "Tarjeta Digital", "Cuenta de Ahorros", "Crédito Rotativo"]
productos = []
for i in range(1, vols["tb_productos_cat"] + 1):
    t_prod = random.choice(tipos)
    productos.append({
        "cod_prod": f"PRD_{i:03d}",
        "desc_prod": f"Producto {t_prod} Tipo {i}",
        "tip_prod": t_prod,
        "tasa_ea": round(random.uniform(0.12, 0.35), 4) if "Crédito" in t_prod else round(random.uniform(0.01, 0.08), 4),
        "plazo_max_meses": random.choice([12, 24, 36, 48, 60]) if "Crédito" in t_prod else 0,
        "cuota_min": random.choice([50000, 100000, 200000]) if "Crédito" in t_prod else 0,
        "comision_admin": random.choice([0, 12000, 25000]),
        "estado_prod": "ACTIVO"
    })
df_productos = pd.DataFrame(productos)

print(">>> [2/6] Generando TB_SUCURSALES_RED...")
ciudades_col = [("Bogotá", "Cundinamarca", 4.7110, -74.0721), 
                ("Medellín", "Antioquia", 6.2442, -75.5812), 
                ("Cali", "Valle del Cauca", 3.4516, -76.5320), 
                ("Barranquilla", "Atlántico", 10.9685, -74.7813), 
                ("Bucaramanga", "Santander", 7.1254, -73.1198)]
sucursales = []
for i in range(1, vols["tb_sucursales_red"] + 1):
    cd = random.choice(ciudades_col)
    sucursales.append({
        "cod_suc": f"SUC_{i:03d}",
        "nom_suc": f"Sucursal {cd[0]} {i}",
        "tip_punto": random.choice(["Física", "Corresponsal", "Kiosco"]),
        "ciudad": cd[0],
        "depto": cd[1],
        "latitud": cd[2] + random.uniform(-0.05, 0.05),
        "longitud": cd[3] + random.uniform(-0.05, 0.05),
        "activo": 1
    })
df_sucursales = pd.DataFrame(sucursales)

print(">>> [3/6] Generando TB_CLIENTES_CORE...")
n_cli = vols["tb_clientes_core"]
scores = np.random.normal(loc=650, scale=80, size=n_cli).clip(300, 850).astype(int)
clientes = []
for i in range(1, n_cli + 1):
    fec_alta = start_dt + timedelta(days=int(np.random.uniform(0, days_range)))
    cd = random.choice(ciudades_col)
    clientes.append({
        "id_cli": i,
        "nomb_cli": fake.first_name(),
        "apell_cli": fake.last_name(),
        "tip_doc": random.choice(["CC", "CE", "TI"]),
        "num_doc": str(random.randint(10000000, 1099999999)),
        "fec_nac": str(fake.date_of_birth(minimum_age=18, maximum_age=75)),
        "fec_alta": fec_alta.strftime("%Y-%m-%d"),
        "cod_segmento": random.choices(["Básico", "Estándar", "Premium", "Elite"], weights=[0.4, 0.35, 0.2, 0.05])[0],
        "score_buro": int(scores[i-1]),
        "ciudad_res": cd[0],
        "depto_res": cd[1],
        "estado_cli": "ACTIVO",
        "canal_adquis": random.choice(["App Móvil", "Web", "Corresponsal"])
    })
df_clientes = pd.DataFrame(clientes)

# Nulos controlados (~5% en ciudad_res)
df_clientes.loc[df_clientes.sample(frac=config["null_rate"], random_state=SEED).index, "ciudad_res"] = None

print(">>> [4/6] Generando TB_OBLIGACIONES...")
n_ob = vols["tb_obligaciones"]
prod_creditos = df_productos[df_productos["tip_prod"].str.contains("Crédito|Tarjeta")]["cod_prod"].values
obligaciones = []
for i in range(1, n_ob + 1):
    vr_aprob = random.choice([2000000, 5000000, 10000000, 20000000])
    sdo_cap = round(vr_aprob * random.uniform(0.1, 0.95), 2)
    fec_des = start_dt + timedelta(days=int(np.random.uniform(0, days_range)))
    dias_mora = int(np.random.exponential(scale=15)) if random.random() < 0.25 else 0
    obligaciones.append({
        "id_oblig": f"OBL_{i:06d}",
        "id_cli": int(np.random.choice(df_clientes["id_cli"])),
        "cod_prod": str(np.random.choice(prod_creditos)),
        "vr_aprobado": vr_aprob,
        "vr_desembolsado": vr_aprob,
        "sdo_capital": sdo_cap,
        "vr_cuota": round(sdo_cap / 24, 2),
        "fec_desembolso": fec_des.strftime("%Y-%m-%d"),
        "fec_venc": (fec_des + timedelta(days=720)).strftime("%Y-%m-%d"),
        "dias_mora_act": dias_mora,
        "num_cuotas_pend": random.randint(1, 24),
        "calif_riesgo": "A" if dias_mora == 0 else ("B" if dias_mora <= 30 else ("C" if dias_mora <= 60 else "D"))
    })
df_obligaciones = pd.DataFrame(obligaciones)

print(">>> [5/6] Generando TB_MOV_FINANCIEROS (500k registros)...")
n_mov = vols["tb_mov_financieros"]
horas_pico = [12, 13, 18, 19, 20]
movs = {
    "id_mov": np.arange(1, n_mov + 1),
    "id_cli": np.random.choice(df_clientes["id_cli"].values, size=n_mov),
    "cod_prod": np.random.choice(df_productos["cod_prod"].values, size=n_mov),
    "num_cuenta": [f"CTA_{random.randint(100000, 999999)}" for _ in range(n_mov)],
    "fec_mov": [(start_dt + timedelta(days=int(d))).strftime("%Y-%m-%d") for d in np.random.uniform(0, days_range, size=n_mov)],
    "hra_mov": [f"{random.choice(horas_pico):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}" for _ in range(n_mov)],
    "vr_mov": np.random.lognormal(mean=10.5, sigma=1.0, size=n_mov).round(2),
    "tip_mov": np.random.choice(["Transferencia", "Pago PSE", "Retiro", "Compra"], size=n_mov),
    "cod_canal": np.random.choice(["App", "Web", "Corresponsal", "Cajero"], size=n_mov),
    "cod_ciudad": np.random.choice(["Bogotá", "Medellín", "Cali", "Barranquilla"], size=n_mov),
    "cod_estado_mov": np.random.choice(["EXITOSO", "RECHAZADO"], p=[0.96, 0.04], size=n_mov),
    "id_dispositivo": [f"DEV_{random.randint(1000, 9999)}" for _ in range(n_mov)]
}
df_movs = pd.DataFrame(movs)

# INYECCIÓN DE 3 ANOMALÍAS INTENCIONALES DOCUMENTADAS
# Anomalía 1: Registros duplicados (10 filas)
df_movs = pd.concat([df_movs, df_movs.iloc[:10]], ignore_index=True)
# Anomalía 2: Fechas futuras fuera de rango (año 2030)
df_movs.loc[15:20, "fec_mov"] = "2030-01-01"
# Anomalía 3: Montos negativos inconsistentes
df_movs.loc[30:35, "vr_mov"] = -50000.00

print(">>> [6/6] Generando TB_COMISIONES_LOG...")
n_com = vols["tb_comisiones_log"]
comisiones = {
    "id_comision": np.arange(1, n_com + 1),
    "id_cli": np.random.choice(df_clientes["id_cli"].values, size=n_com),
    "cod_prod": np.random.choice(df_productos["cod_prod"].values, size=n_com),
    "fec_cobro": [(start_dt + timedelta(days=int(d))).strftime("%Y-%m-%d") for d in np.random.uniform(0, days_range, size=n_com)],
    "vr_comision": np.random.choice([3500.0, 5500.0, 12000.0, 25000.0], size=n_com),
    "tip_comision": np.random.choice(["Cuota Manejo", "Avance", "Transferencia ACH"], size=n_com),
    "estado_cobro": np.random.choice(["COBRADO", "EXONERADO"], p=[0.9, 0.1], size=n_com)
}
df_comisiones = pd.DataFrame(comisiones)

print(">>> Exportando en múltiples formatos (CSV, Parquet, JSON)...")
# Formato JSON
df_productos.to_json(os.path.join(out_dir, "TB_PRODUCTOS_CAT.json"), orient="records", indent=2)
# Formato CSV
df_sucursales.to_csv(os.path.join(out_dir, "TB_SUCURSALES_RED.csv"), index=False, encoding="utf-8-sig")
df_clientes.to_csv(os.path.join(out_dir, "TB_CLIENTES_CORE.csv"), index=False, encoding="utf-8-sig")
# Formato Parquet (Altamente eficiente para Big Data)
df_obligaciones.to_parquet(os.path.join(out_dir, "TB_OBLIGACIONES.parquet"), index=False)
df_movs.to_parquet(os.path.join(out_dir, "TB_MOV_FINANCIEROS.parquet"), index=False)
df_comisiones.to_parquet(os.path.join(out_dir, "TB_COMISIONES_LOG.parquet"), index=False)

print(">>> ¡Generación de datos finalizada exitosamente en data-generation/data/!")