
variable "service_name" {
  description = "OVHCloud project ID — found in the OVH console URL"
  type        = string
  # Never put the actual value here
  # Set it via TF_VAR_service_name environment variable
}

variable "project_name" {
  description = "Project prefix for all resource names"
  type        = string
  default     = "ecom-platform"
}

variable "allowed_ip_ranges" {
  description = "IP ranges allowed to reach managed Postgres"
  type        = list(string)
  default     = []
}