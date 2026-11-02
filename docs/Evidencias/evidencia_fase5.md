# Evidencias de Gobierno y Seguridad - Fase 5 (RBAC y Catálogo)

Implementación de controles de gobierno de datos, privacidad y seguridad de acceso en Microsoft Azure.

### 1. Control de Acceso Basado en Roles (RBAC) en Azure
Evidencia de asignación exclusiva del rol **`Storage Blob Data Reader`** (Analista de Negocio) con alcance restringido únicamente al contenedor `gold` (*This resource*):
![RBAC Gold Container](Evidencias/08_rbac_analista_gold.png)

### 2. Cumplimiento de Principio de Menor Privilegio
* **Administrador (`Owner`):** Control del Resource Group y ciclo de vida.
* **Ingeniero de Datos (`Storage Blob Data Contributor`):** Lectura/escritura en todas las capas del Data Lake.
* **Analista (`Storage Blob Data Reader`):** Acceso exclusivo a la capa Gold para consumo de reportes; acceso restringido y denegado en Bronze y Silver para proteger datos crudos y PII.

### 3. Privacidad y Seguridad (Habeas Data)
* Pseudonimización criptográfica irreversible mediante **SHA-256** sobre documentos de identidad (`num_doc`).
* Custodia de cadenas de conexión y credenciales mediante **Azure Key Vault** (`kv-finbank-rch7`).