terraform {
  required_version = ">= 1.9.0"

  required_providers {
    ovh = {
      source  = "ovh/ovh"
      version = "~> 2.1"
    }
  }

  backend "s3" {
    bucket = "ecom-terraform-state-pre-prod"
    key    = "pre-prod/terraform.tfstate"
    region = "eu-west-par"
    endpoints = {
      s3 = "https://s3.eu-west-par.io.cloud.ovh.net"
    }
    skip_credentials_validation = true
    skip_region_validation      = true
    skip_requesting_account_id  = true
  }
}

provider "ovh" {
  endpoint = "ovh-eu"
}

module "kubernetes" {
  source = "../../modules/kubernetes-cluster"

  service_name       = var.service_name
  cluster_name       = var.project_name
  environment        = "pre-prod"
  region             = "GRA9"
  kubernetes_version = var.kubernetes_version
  node_flavor        = "b3-8"
  node_count         = 3 # more than dev, mirrors prod resilience
  vlan_id            = var.vlan_id

  tags = {
    project = var.project_name
    env     = "pre-prod"
  }
}

module "warehouse_storage" {
  source = "../../modules/object-storage"

  service_name       = var.service_name
  bucket_name        = "${var.project_name}-warehouse"
  environment        = "pre-prod"
  region             = "GRA"
  versioning_enabled = true # enabled — mirrors prod behavior
}

module "postgres" {
  source = "../../modules/managed-postgres"

  service_name      = var.service_name
  environment       = "pre-prod"
  region            = "GRA"
  plan              = "essential" # same plan as prod — catch plan-specific bugs
  flavor            = "db1-4"     # larger than dev
  postgres_version  = "15"
  allowed_ip_ranges = var.allowed_ip_ranges
}
