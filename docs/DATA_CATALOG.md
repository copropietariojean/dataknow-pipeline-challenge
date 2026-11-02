# Catálogo de Datos y Gobierno - FinBank S.A.

## 1. Matriz de Roles y Control de Acceso (RBAC)

Se implementó el principio de menor privilegio (*Least Privilege*) en Microsoft Azure:

| Rol | Capas con Acceso | Permisos | Justificación de Negocio |
| :--- | :--- | :--- | :--- |
| **Administrador** | Todas (`bronze`, `silver`, `gold`, `infra`) | Control Total (`Owner`) | Gestión de suscripción, presupuestos y recursos cloud. |
| **Ingeniero de Datos** | `bronze`, `silver`, `gold` | Lectura y Escritura (`Storage Blob Data Contributor`) | Construcción, depuración y mantenimiento de pipelines ETL/ELT. |
| **Analista de Negocio** | Exclusivamente `gold` | Solo Lectura (`Storage Blob Data Reader`) | Consumo analítico de KPIs y dashboards. Acceso denegado a Bronze y Silver para proteger datos crudos y PII. |

---

## 2. Clasificación de Datos y Privacidad (PII)

| Campo Origen | Tabla | Tipo | Clasificación | Tratamiento de Seguridad |
| :--- | :--- | :--- | :--- | :--- |
| `num_doc` | `TB_CLIENTES_CORE` | String | **Sensible (PII)** | Pseudonimizado en Capa Silver mediante Hash Criptográfico **SHA-256** (`num_doc_hash`). |
| `nomb_cli` / `apell_cli` | `TB_CLIENTES_CORE` | String | Confidencial | Unificado en `nombre_completo` para analítica; restringido al perfil Analista. |
| `vr_mov` | `TB_MOV_FINANCIEROS` | Decimal | Financiero | Convertido a USD en Gold; transacciones atípicas marcadas con `ind_sospechoso`. |

---

## 3. Diccionario de Datos (Capa Gold)

### Dimensión Clientes (`dim_clientes`)
* `id_cli` (Int, PK): Identificador único del cliente.
* `nombre_completo` (String): Nombres y apellidos limpios y unificados.
* `num_doc_hash` (String): Hash SHA-256 de la cédula para cruces analíticos seguros.
* `edad` (Int): Edad calculada a partir de la fecha de nacimiento.
* `cod_segmento` (String): Categoría comercial (Básico, Estándar, Premium, Elite).
* `score_buro` (Int): Puntaje de riesgo crediticio (300 a 850).
* `ciudad_res` (String): Ciudad de residencia (imputada como "NO REPORTADA" ante nulos).

### Tabla de Hechos Cartera (`fact_cartera`)
* `id_oblig` (String, PK): Código único del crédito o tarjeta.
* `id_cli` (Int, FK): Llave foránea hacia `dim_clientes`.
* `cod_prod` (String, FK): Llave foránea hacia `dim_productos`.
* `vr_aprobado` (Decimal): Monto original aprobado del crédito.
* `sdo_capital` (Decimal): Saldo pendiente de pago.
* `dias_mora_act` (Int): Días de atraso en el pago.
* `bucket_mora` (String): Tramo de mora regulatorio calculado.
* `provision_estimada` (Decimal): Dinero en reserva exigido por riesgo de impago.

---

## 4. Linaje de Datos de Campos Calculados (Data Lineage)

### Campo 1: `bucket_mora` (`fact_cartera`)
* **Tabla Origen:** `TB_OBLIGACIONES` (`dias_mora_act`).
* **Transformación:** Regla condicional de negocio en 5 tramos:
  * $0 \rightarrow$ "Al día"
  * $1\text{ a }30 \rightarrow$ "Rango 1 (1-30 días)"
  * $31\text{ a }60 \rightarrow$ "Rango 2 (31-60 días)"
  * $61\text{ a }90 \rightarrow$ "Rango 3 (61-90 días)"
  * $>90 \rightarrow$ "Deteriorado (>90 días)"
* **Propósito:** Segmentar la salud crediticia de la cartera para el Comité de Riesgo.

### Campo 2: `provision_estimada` (`fact_cartera`)
* **Tablas Origen:** `TB_OBLIGACIONES` (`sdo_capital` y `dias_mora_act`).
* **Transformación:** `sdo_capital` $\times$ `porc_provision` (1% para Al día, 5% Rango 1, 20% Rango 2, 50% Rango 3, 100% Deteriorado).
* **Propósito:** Cumplimiento de provisiones normativas de la Superintendencia Financiera.

### Campo 3: `tasa_mora_porc` (`kpi_diarios_cartera`)
* **Tablas Origen:** `fact_cartera` agrupada por fecha, producto y ciudad.
* **Transformación:** $\frac{\sum \text{Saldo en Mora}}{\sum \text{Saldo Total de Cartera}} \times 100$.
* **Propósito:** Indicador ejecutivo diario para detectar deterioro temprano en regiones.