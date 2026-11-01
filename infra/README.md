# Infraestructura como Código (IaC) - FinBank Azure

Este módulo de Terraform aprovisiona la arquitectura base para la plataforma de datos bancaria en Microsoft Azure, garantizando seguridad, reproducibilidad y gobernanza de costos (*FinOps*).

## Recursos Aprovisionados

| Recurso | Tipo en Azure | Región | Propósito en la Solución |
| :--- | :--- | :--- | :--- |
| **`rg-finbank-dev`** | Resource Group | East US 2 | Contenedor lógico central para gobernanza y ciclo de vida. |
| **`stfinbankdevrch7`** | Storage Account (ADLS Gen2) | East US 2 | Data Lake jerárquico con contenedores `bronze`, `silver` y `gold`. |
| **`adf-finbank-dev-rch7`** | Data Factory V2 | East US 2 | Motor de orquestación e ingesta automatizada. |
| **`kv-finbank-rch7`** | Key Vault | East US 2 | Almacén centralizado de secretos y cadenas de conexión. |
| **`law-finbank-dev`** | Log Analytics Workspace | East US 2 | Auditoría, observabilidad y trazabilidad operativa. |
| **`ag-finbank-alerts`** | Action Group | Global | Notificaciones automáticas por correo ante incidencias. |

## Instrucciones de Despliegue

1. Autenticar la sesión en Azure CLI:
   ```bash
   az login
   project_name = "finbank"
environment  = "dev"
location     = "eastus2"
alert_email  = "jeanmichell.romero@hotmail.com"

2. Inicializar y desplegar:
terraform init
terraform plan
terraform apply