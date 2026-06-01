variable "service_name" {
  description = "OVHCloud project ID (service_name) — found in the OVH console URL"
  type        = string

  validation {
    # OVHCloud project IDs are hexadecimal strings
    condition     = length(var.service_name) > 0
    error_message = "service_name cannot be empty — check your OVH console URL"
  }
}

variable "cluster_name" {
  description = "ecom-ai"
  type        = string
}

variable "environment" {
  description = "Deployment environment: dev | pre-prod | prod"
  type        = string

  validation {
    condition     = contains(["dev", "pre-prod", "prod"], var.environment)
    error_message = "environment must be one of: dev, pre-prod, prod"
  }
}

variable "region" {
  description = "OVHCloud region"
  type        = string
  default     = "GRA9" 
}

variable "kubernetes_version" {
  description = "Kubernetes version — check available versions in OVH console"
  type        = string
  default     = "1.31"
}

variable "node_flavor" {
  description = "OVHCloud node flavor (machine size)"
  type        = string
  # Available flavors: https://www.ovhcloud.com/en/public-cloud/prices/
  # b3-8  = 4 vCPU, 8GB  RAM  — good for dev
  # b3-32 = 8 vCPU, 32GB RAM  — good for prod (Trino is memory-hungry)
}

variable "node_count" {
  description = "Number of worker nodes"
  type        = number

  validation {
    condition     = var.node_count >= 1 && var.node_count <= 10
    error_message = "node_count must be between 1 and 10"
  }
}

variable "tags" {
  description = "Tags applied to all resources"
  type        = map(string)
  default     = {}
}

variable "network_region" {
  description = "OVH region for private network — uppercase full name (EU-WEST-PAR)"
  type        = string
  default     = "GRA9"
}