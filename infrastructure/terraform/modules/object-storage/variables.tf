
variable "bucket_name" {
  description = "Name of the S3-compatible bucket"
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

variable "service_name" {
  description = "OVHCloud project ID (service_name)"
  type        = string
}

variable "versioning_enabled" {
  description = "Enable object versioning — recommended for Iceberg warehouse"
  type        = bool
  default     = false
}