variable "service_name" {
  description = "OVHCloud project ID"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "region" {
  description = "OVHCloud region"
  type        = string
  default     = "GRA"
}

variable "plan" {
  description = "Database plan: essential | business | enterprise"
  type        = string
  default     = "essential"

  validation {
    condition     = contains(["essential", "business", "enterprise"], var.plan)
    error_message = "plan must be essential, business, or enterprise"
  }
}

variable "flavor" {
  description = "Node flavor for the database"
  type        = string
  default     = "db1-4"
}

variable "postgres_version" {
  description = "PostgreSQL major version"
  type        = string
  default     = "15"
}

variable "allowed_ip_ranges" {
  description = "IP ranges allowed to connect to the database"
  type        = list(string)
  default     = []
}