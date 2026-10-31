# Evidencia de Carga Exitosa - Fase 1 (Base de Datos Relacional)

Se realizó la carga exitosa de las tablas origen en el motor relacional SQLite (`finbank_source.db`) a partir de archivos heterogéneos (CSV, JSON, Parquet).

### Conteo Oficial (`SELECT COUNT(*)`):

| Tabla Origen | Volumen Mínimo Exigido | Registros Cargados | Formato Origen | Cumplimiento |
| :--- | :--- | :--- | :--- | :--- |
| **TB_CLIENTES_CORE** | 10.000 | 10.000 | CSV (`utf-8-sig`) | Cumple (100%) |
| **TB_PRODUCTOS_CAT** | 50 | 50 | JSON | Cumple (100%) |
| **TB_SUCURSALES_RED** | 200 | 200 | CSV (`utf-8-sig`) | Cumple (100%) |
| **TB_OBLIGACIONES** | 30.000 | 30.000 | Parquet | Cumple (100%) |
| **TB_MOV_FINANCIEROS** | 500.000 | 500.010 | Parquet | Cumple (100% + 10 duplicados de prueba) |
| **TB_COMISIONES_LOG** | 80.000 | 80.000 | Parquet | Cumple (100%) |

**Total Registros Generados y Almacenados:** 620.260 filas.