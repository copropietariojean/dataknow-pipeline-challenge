variable "project_name" {
  type        = string
  default     = "finbank"
  description = "Nombre base del proyecto bancario"
}

variable "environment" {
  type        = string
  default     = "dev"
  description = "Ambiente de despliegue (dev / prod)"
}

variable "location" {
  type        = string
  default     = "eastus2"
  description = "Región de Azure (East US 2 optimizada en costos)"
}

variable "alert_email" {
  type        = string
  default     = "tu_correo@ejemplo.com" # Cambiaremos esto con un archivo seguro
  description = "Correo que recibe las alertas de monitoreo"
}