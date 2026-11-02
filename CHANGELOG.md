# Historial de Cambios (Changelog) - FinBank Data Pipeline

Todas las modificaciones notables de este proyecto están documentadas en este archivo según el estándar *Keep a Changelog*.

## [1.0.0] - 2026-11-02
### Autor: Jean Michell Leguizamón Romero

### Agregado (Fase 5 - Gobierno, Seguridad y Calidad)
- Implementación de matriz de roles RBAC con principio de menor privilegio (Administrador, Ingeniero de Datos, Analista).
- Publicación del Catálogo de Datos oficial en `/docs/DATA_CATALOG.md` con clasificación de información sensible (PII).
- Documentación formal del linaje de datos para campos calculados clave (`bucket_mora`, `provision_estimada`, `tasa_mora_porc`).
- Documentación maestra del repositorio en `README.md` con arquitectura, justificaciones y guía de reproducción.

### Agregado (Fase 4 - Orquestación del Pipeline)
- Orquestador automatizado `pipeline_orchestrator.py` con dependencias estrictas (DAG: Bronze -> Silver -> Gold -> Data Quality).
- Mecanismo de tolerancia a fallos con reintentos automáticos (máximo 3) y espera por backoff exponencial ($2^n$).
- Generación de logs operacionales en `/orchestration/logs/` y reporte diario de ejecución.

### Agregado (Fase 3 - Arquitectura Medallón en Azure Data Lake)
- Ingesta cruda en Capa Bronze (`bronze_ingestion.py`) con metadatos de auditoría (`fecha_ingesta`, `sistema_fuente`, `id_lote`) y particionamiento por fecha (`year/month/day`).
- Capa Silver (`silver_transformation.py`) con deduplicación exacta, enmascaramiento criptográfico SHA-256 para cédulas, aislamiento de anomalías en `TB_ERRORES_PIPELINE` y detección estadística de transacciones sospechosas.
- Capa Gold (`gold_aggregation.py`) con modelo dimensional en estrella (`dim_clientes`, `dim_productos`, `dim_geografia`, `dim_canal`, `fact_cartera`, `fact_transacciones`) y tabla ejecutiva de KPIs diarios.
- Suite automatizada de pruebas de calidad (`data_quality_tests.py`) con 5 aserciones críticas aprobadas al 100%.

### Agregado (Fase 2 - Infraestructura como Código con Terraform)
- Aprovisionamiento en Microsoft Azure (`rg-finbank-dev`, región `eastus2`):
  - Storage Account con ADLS Gen2 habilitado (`is_hns_enabled`) y contenedores `bronze`, `silver`, `gold`.
  - Azure Data Factory V2 con identidad administrada asignada por el sistema.
  - Azure Key Vault estándar para custodia de secretos.
  - Log Analytics Workspace (retención 30 días) y Action Group para alertas operativas por correo.
- Modularización de IaC en `main.tf`, `variables.tf`, `providers.tf`, `outputs.tf` y `terraform.tfvars`.

### Agregado (Fase 1 - Generación de Datos Sintéticos y Origen Relacional)
- Script parametrizado `generate_data.py` con semilla fija (`seed: 42`) para garantizar reproducibilidad e idempotencia.
- Generación de 620.260 registros en formatos heterogéneos (CSV con UTF-8-SIG, JSON, Parquet).
- Inyección documentada de valores nulos (5%) y 3 anomalías intencionales (duplicados, fechas en 2030, importes negativos).
- Esquema relacional DDL (`schema.sql`) y carga automatizada a SQLite (`finbank_source.db`).
- Diagrama Entidad-Relación en formato Docs-as-Code (`ER_DIAGRAM.md` con Mermaid).