terraform {
  required_providers {
    ovh = {
      source  = "ovh/ovh"
      version = "~> 2.1"
    }
  }
}

# ============================================================
# OVHCloud S3-compatible Object Storage bucket
# ovh_cloud_project_storage available from provider ~> 2.1
# ============================================================

resource "ovh_cloud_project_storage" "main" {
  service_name = var.service_name
  region_name  = upper(var.region)
  name         = "${var.bucket_name}-${var.environment}"

  versioning = {
    status = var.versioning_enabled ? "enabled" : "suspended"
  }

  encryption = {
    sse_algorithm = "AES256"
  }
}

# ============================================================
# S3 user + credentials scoped to this project
# ============================================================

resource "ovh_cloud_project_user" "s3_user" {
  service_name = var.service_name
  description  = "s3-user-${var.bucket_name}-${var.environment}"
  role_names   = ["objectstore_operator"]
}

resource "ovh_cloud_project_user_s3_credential" "main" {
  service_name = var.service_name
  user_id      = ovh_cloud_project_user.s3_user.id
}