# Obtener información del usuario autenticado actualmente (sin quemar IDs)
data "azurerm_client_config" "current" {}

# Sufijo aleatorio de 4 caracteres para garantizar nombres únicos a nivel mundial
resource "random_string" "suffix" {
  length  = 4
  special = false
  upper   = false
}

# 1. GRUPO DE RECURSOS (La carpeta contenedora de todo el banco)
resource "azurerm_resource_group" "rg" {
  name     = "rg-${var.project_name}-${var.environment}"
  location = var.location

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# 2. DATA LAKE STORAGE GEN2 (El disco duro Big Data con bronze, silver y gold)
resource "azurerm_storage_account" "datalake" {
  name                     = "st${var.project_name}${var.environment}${random_string.suffix.result}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS" # La opción más económica (FinOps)
  is_hns_enabled           = true  # HABILITA ADLS Gen2 (Estructura jerárquica obligatoria)

  tags = azurerm_resource_group.rg.tags
}

# Contenedores para la Arquitectura Medallón
resource "azurerm_storage_data_lake_gen2_filesystem" "containers" {
  for_each           = toset(["bronze", "silver", "gold"])
  name               = each.key
  storage_account_id = azurerm_storage_account.datalake.id
}

# 3. AZURE DATA FACTORY (El motor de orquestación y movimiento de datos)
resource "azurerm_data_factory" "adf" {
  name                = "adf-${var.project_name}-${var.environment}-${random_string.suffix.result}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  identity {
    type = "SystemAssigned" # Identidad propia sin contraseñas (Principio de menor privilegio)
  }

  tags = azurerm_resource_group.rg.tags
}

# 4. AZURE KEY VAULT (Bóveda de máxima seguridad para credenciales)
resource "azurerm_key_vault" "kv" {
  name                        = "kv-${var.project_name}-${random_string.suffix.result}"
  location                    = azurerm_resource_group.rg.location
  resource_group_name         = azurerm_resource_group.rg.name
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  sku_name                    = "standard"
  soft_delete_retention_days  = 7
  purge_protection_enabled    = false

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    secret_permissions = [
      "Get", "List", "Set", "Delete", "Purge"
    ]
  }

  tags = azurerm_resource_group.rg.tags
}

# 5. LOG ANALYTICS WORKSPACE (Monitoreo y auditoría centralizada)
resource "azurerm_log_analytics_workspace" "law" {
  name                = "law-${var.project_name}-${var.environment}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
  retention_in_days   = 30

  tags = azurerm_resource_group.rg.tags
}

# 6. ACTION GROUP (Sistema de alertas automáticas ante fallas)
resource "azurerm_monitor_action_group" "alerts" {
  name                = "ag-${var.project_name}-alerts"
  resource_group_name = azurerm_resource_group.rg.name
  short_name          = "finbankalert"

  email_receiver {
    name                    = "AdminEmail"
    email_address           = var.alert_email
    use_common_alert_schema = true
  }

  tags = azurerm_resource_group.rg.tags
}