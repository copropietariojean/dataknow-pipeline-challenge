# Evidencias de Despliegue en Nube - Fase 2 (IaC Azure)

Aprovisionamiento exitoso mediante Terraform de la infraestructura para FinBank S.A. en Microsoft Azure.

### 1. Salida de Terminal (`terraform apply`)
Evidencia de ejecución exitosa con 10 recursos creados y exportación de outputs sin errores:
![Terraform Apply](Evidencias/01_terraform_apply_exitoso.png)

### 2. Entorno en Microsoft Azure Portal
Grupo de recursos `rg-finbank-dev` activo con sus etiquetas de gobernanza (*Tags*):
![Azure Portal](Evidencias/02_recursos_azure_portal.png)

### 3. Contenedores del Data Lake (ADLS Gen2)
Estructura de almacenamiento de la Arquitectura Medallón lista para ingesta:
![Contenedores ADLS Gen2](Evidencias/03_contenedores_adls_gen2.png)