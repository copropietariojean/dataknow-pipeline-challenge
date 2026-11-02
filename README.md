# FinBank S.A. — End-to-End Cloud Data Platform (DataKnow Challenge)

Solución integral de arquitectura e ingeniería de datos para la modernización analítica de **FinBank S.A.** en **Microsoft Azure**, implementando principios de Infraestructura como Código (IaC), Arquitectura Medallón (Bronze, Silver, Gold), Orquestación tolerante a fallos y Gobierno de Datos con observabilidad en tiempo real.

---

## 1. Declaración Inicial y Justificación Técnica de Decisiones

### Sector de Negocio Elegido
* **Escenario A: Banca y Servicios Financieros (FinBank S.A.)**
* **Justificación de Negocio:** Permite abordar retos de alto impacto en el sector bancario: monitoreo de deterioro de cartera crediticia mediante cálculo de *buckets* de mora y provisiones regulatorias (Superintendencia Financiera), detección preventiva de fraudes transaccionales mediante algoritmos estadísticos de valores atípicos (*outliers*), y medición del valor del cliente en el tiempo (*Customer Lifetime Value - CLTV*).

### Plataforma Cloud Seleccionada
* **Microsoft Azure**
* **Justificación de Arquitectura:** 
  1. **Capacidades Analíticas de ADLS Gen2:** Almacenamiento jerárquico (*Hierarchical Namespace*) que optimiza operaciones atómicas de directorios y reduce costos de lectura mediante *Partition Pruning*.
  2. **Gobernanza y FinOps Nativo:** Monitoreo presupuestal preventivo con alertas automatizadas antes de la ejecución de cómputo, y gestión centralizada de secretos mediante Azure Key Vault.
  3. **Seguridad Empresarial:** Control de acceso granular por roles (RBAC) a nivel de contenedor para proteger información sensible y asegurar el principio de menor privilegio.

---

## 2. Arquitectura de la Solución

```mermaid
flowchart TD
    subgraph Origen ["1. Sistema Transaccional Origen"]
        SQL[("Base de Datos Relacional\n(finbank_source.db)")]
    end

    subgraph IaC ["2. Infraestructura como Código (Terraform)"]
        TF["Terraform Plan & Apply\n(rg-finbank-dev)"]
    end

    subgraph Lakehouse ["3. Azure Data Lake Storage Gen2 (stfinbankdevrch7)"]
        Bronze[("Capa Bronze\n(Parquet Crudo + Partición Fecha\n+ Metadatos Auditoría)")]
        Silver[("Capa Silver\n(Deduplicado + SHA-256 PII\n+ Regla Fraude Outliers)")]
        Gold[("Capa Gold\n(Modelo Dimensional Estrella\n+ Provisiones Mora + CLTV)")]
        Errors[("Cuarentena de Anomalías\n(TB_ERRORES_PIPELINE)")]
    end

    subgraph Orquestacion ["4. Orquestación y Observabilidad"]
        DAG["Orquestador Secuencial\n(02:00 AM / Backoff Exponencial)"]
        Logs["Log Analytics & Logs Locales"]
        Alerts["Action Group (Alertas Email)"]
    end

    subgraph Gobierno ["5. Gobierno y Consumo"]
        RBAC["Control de Acceso RBAC\n(Analista: Solo Gold\nIngeniero: Bronze/Silver/Gold)"]
        KPIs["Tablas Ejecutivas de Cartera\n(Comité de Riesgo)"]
    end

    SQL -->|Ingesta Batch| Bronze
    Bronze -->|Limpieza y Encriptación| Silver
    Silver -->|Rechazos / Fechas Futuras| Errors
    Silver -->|Modelo Dimensional| Gold
    DAG -->|Coordina Flujo| Bronze
    DAG -->|Coordina Flujo| Silver
    DAG -->|Coordina Flujo| Gold
    Gold --> KPIs
    Gold --> RBAC
    DAG --> Logs
    DAG --> Alerts

## 3. Estructura del Repositorio

dataknow-pipeline-challenge/
│
├── infra/                      # Código IaC con Terraform para Azure
│   ├── main.tf                 # Definición de recursos (RG, ADLS, ADF, KV, LAW, Alerts)
│   ├── variables.tf            # Variables parametrizadas
│   ├── providers.tf            # Proveedor azurerm
│   ├── outputs.tf              # Endpoints y nombres generados
│   ├── terraform.tfvars        # Parámetros del entorno dev
│   └── README.md               # Guía de despliegue de infraestructura
│
├── data-generation/            # Generación de datos sintéticos y origen relacional
│   ├── config.json             # Parámetros, semilla fija (seed: 42) y volúmenes
│   ├── generate_data.py        # Generador de 620k registros con anomalías documentadas
│   ├── schema.sql              # Estructura relacional DDL origen
│   ├── load_to_sql.py          # Script de carga a base de datos SQLite
│   └── finbank_source.db       # Motor relacional fuente
│
├── pipelines/                  # Pipeline end-to-end (Arquitectura Medallón)
│   ├── bronze_ingestion.py     # Ingesta cruda con partición y metadatos de auditoría
│   ├── silver_transformation.py# Deduplicación, hash SHA-256, tabla de errores y fraude
│   ├── gold_aggregation.py     # Modelo estrella, mora, provisiones, KPIs y CLTV
│   └── data_quality_tests.py   # Suite automatizada de 5 pruebas de calidad (100% Pass)
│
├── orchestration/              # Automatización y gestión de flujos de trabajo
│   ├── pipeline_orchestrator.py# DAG con dependencias, reintentos y reporte diario
│   └── logs/                   # Histórico de ejecución y auditoría
│
├── docs/                       # Documentación técnica y evidencias fotográficas
│   ├── ER_DIAGRAM.md           # Diagrama ER interactivo en Mermaid
│   ├── DATA_CATALOG.md         # Catálogo de datos, roles RBAC y linaje
│   ├── evidencia_fase1.md      # Conteo SELECT COUNT(*) por tabla
│   ├── evidencia_fase2.md      # Aprovisionamiento IaC en Azure
│   ├── evidencia_fase3.md      # Pipeline Medallón y Data Quality
│   ├── evidencia_fase4.md      # Orquestación y ejecución de tareas
│   ├── evidencia_fase5.md      # Permisos RBAC y seguridad en Azure
│   └── Evidencias/             # Capturas de pantalla oficiales en alta resolución
│
├── CHANGELOG.md                # Bitácora de versiones según Keep a Changelog
├── .gitignore                  # Protección de secretos (*.tfstate, .env)
└── README.md                   # Documentación principal de la solución


## 4. Guía de Reproducción Paso a Paso
Para desplegar y reproducir la solución completa en cualquier máquina:
1. Clonar el repositorio e instalar dependencias:
git clone https://github.com/copropietariojean/dataknow-pipeline-challenge.git
cd dataknow-pipeline-challenge
python -m pip install pandas faker pyarrow azure-storage-blob azure-identity

2. Generar datos y cargar base de datos relacional fuente (Fase 1):
python data-generation/generate_data.py
python data-generation/load_to_sql.py

3. Aprovisionar infraestructura en Microsoft Azure (Fase 2):
az login
cd infra
terraform init
terraform plan
terraform apply -auto-approve
cd ..

4. Ejecutar el orquestador del pipeline bancario (Fases 3 y 4):
python orchestration/pipeline_orchestrator.py

5. Validar suite de calidad de datos:
python pipelines/data_quality_tests.py


## 5. Resumen de Evidencias en Nube (Azure)
Todas las evidencias gráficas detalladas están documentadas en /docs/:
1. Despliegue IaC en Azure: docs/Evidencias/01_terraform_apply_exitoso.png y 02_recursos_azure_portal.png
2. Estructura Data Lake Gen2: docs/Evidencias/03_contenedores_adls_gen2.png
3. Ingesta Capa Bronze: docs/Evidencias/04_ingesta_bronze_azure.png
4. Transformación Capa Silver & Cuarentena: docs/Evidencias/05_transformacion_silver_azure.png
5. Modelo Dimensional Capa Gold: docs/Evidencias/06_modelo_dimensional_gold_azure.png
6. Orquestación y Logs Operacionales: docs/Evidencias/07_orquestacion_dag_exitoso.png
7. Control de Acceso RBAC (Analista en Gold): docs/Evidencias/08_rbac_analista_gold.png


Autor
Jean Michell Romero
Ingeniería y Arquitectura de Datos




