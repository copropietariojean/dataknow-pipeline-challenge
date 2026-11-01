output "resource_group_name" {
  description = "Nombre del Grupo de Recursos creado en Azure"
  value       = azurerm_resource_group.rg.name
}

output "storage_account_name" {
  description = "Nombre único de la cuenta de almacenamiento ADLS Gen2"
  value       = azurerm_storage_account.datalake.name
}

output "storage_primary_dfs_endpoint" {
  description = "Punto de conexión del Data Lake para Big Data"
  value       = azurerm_storage_account.datalake.primary_dfs_endpoint
}

output "data_factory_name" {
  description = "Nombre de la instancia de Azure Data Factory"
  value       = azurerm_data_factory.adf.name
}

output "key_vault_uri" {
  description = "Dirección URI del Azure Key Vault para consultar secretos"
  value       = azurerm_key_vault.kv.vault_uri
}

output "log_analytics_workspace_id" {
  description = "ID del espacio de trabajo de Log Analytics"
  value       = azurerm_log_analytics_workspace.law.id
}