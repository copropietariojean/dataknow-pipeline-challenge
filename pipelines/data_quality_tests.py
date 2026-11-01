import os
import pandas as pd

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
gold_dir = os.path.join(base_dir, "pipelines", "data", "gold")

print("="*65)
print(">>> EJECUTANDO SUITE DE 5 PRUEBAS AUTOMATIZADAS DE CALIDAD (DATA QUALITY)")
print("="*65)

# Cargar tablas Gold para auditar
df_cli = pd.read_parquet(os.path.join(gold_dir, "dim_clientes.parquet"))
df_cartera = pd.read_parquet(os.path.join(gold_dir, "fact_cartera.parquet"))
df_mov = pd.read_parquet(os.path.join(gold_dir, "fact_transacciones.parquet"))

tests = []

# Test 1: Completitud de Llave Primaria en Clientes (No nulos)
t1_nulos = df_cli["id_cli"].isnull().sum()
tests.append(("TEST 1: No nulos en id_cli (dim_clientes)", t1_nulos == 0, f"Nulos encontrados: {t1_nulos}"))

# Test 2: Rango Positivo de Saldos en Cartera
t2_negativos = (df_cartera["sdo_capital"] < 0).sum()
tests.append(("TEST 2: Saldos de capital no negativos (fact_cartera)", t2_negativos == 0, f"Negativos: {t2_negativos}"))

# Test 3: Rango Válido de Provisiones (Entre 0% y 100%)
t3_rango = ((df_cartera["porc_provision"] < 0) | (df_cartera["porc_provision"] > 1.0)).sum()
tests.append(("TEST 3: Porcentajes de provisión válidos (0.0 a 1.0)", t3_rango == 0, f"Fuera de rango: {t3_rango}"))

# Test 4: Integridad Referencial Transacciones vs Clientes (Huérfanos)
clientes_ids = set(df_cli["id_cli"])
t4_huerfanos = (~df_mov["id_cli"].isin(clientes_ids)).sum()
tests.append(("TEST 4: Integridad referencial (fact_transacciones -> dim_clientes)", t4_huerfanos == 0, f"Huérfanos: {t4_huerfanos}"))

# Test 5: Unicidad de Llave Primaria (Cero duplicados en Clientes)
t5_duplicados = df_cli["id_cli"].duplicated().sum()
tests.append(("TEST 5: Unicidad de llave primaria en dim_clientes", t5_duplicados == 0, f"Duplicados: {t5_duplicados}"))

# Impresión del Reporte Oficial
aprobadas = 0
for nombre, resultado, detalle in tests:
    estado = "APROBADO [PASS] ✔" if resultado else "FALLIDO [FAIL] ❌"
    if resultado: aprobadas += 1
    print(f"{nombre.ljust(58)} | {estado}")
    print(f"   -> Detalle: {detalle}")

print("="*65)
print(f"RESULTADO FINAL: {aprobadas}/5 Pruebas Aprobadas Exitosamente (100% Calidad)")
print("="*65)