terraform {
  required_providers {
    ovh = {
      source  = "ovh/ovh"
      version = "~> 2.1"
    }
  }
}

# ============================================================
# OVHCloud Managed PostgreSQL
# In "essential" plan — no private network support
# Private network only available on "business" plan and above
# ============================================================

resource "ovh_cloud_project_database" "postgres" {
  service_name = var.service_name
  description  = "ecom-postgres-${var.environment}"
  engine       = "postgresql"
  version      = var.postgres_version
  plan         = var.plan
  flavor       = var.flavor

  nodes {
    # essential plan = public endpoint only, no network_id
    region = upper(var.region)
  }

  dynamic "ip_restrictions" {
    for_each = var.allowed_ip_ranges
    content {
      ip          = ip_restrictions.value
      description = "Allowed for ${var.environment}"
    }
  }
}

resource "ovh_cloud_project_database_postgresql_user" "app_user" {
  service_name = var.service_name
  cluster_id   = ovh_cloud_project_database.postgres.id
  name         = "ecom_app"
}