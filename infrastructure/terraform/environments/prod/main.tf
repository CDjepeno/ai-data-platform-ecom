terraform {
  required_version = ">= 1.9.0"

  required_providers {
    ovh = {
      source  = "ovh/ovh"
      version = "~> 2.1"
    }
  }

  backend "s3" {
    bucket = "ecom-terraform-state-prod"
    key    = "prod/terraform.tfstate"
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
  environment        = "prod"
  region             = "GRA9"
  kubernetes_version = "1.31"
  node_flavor        = "b3-16"   # larger flavor for production load
  node_count         = 3         # minimum 3 nodes for HA

  tags = {
    project = var.project_name
    env     = "prod"
  }
}

module "warehouse_storage" {
  source = "../../modules/object-storage"

  service_name       = var.service_name
  bucket_name        = "${var.project_name}-warehouse"
  environment        = "prod"
  region             = "GRA"
  versioning_enabled = true     # mandatory in prod — enables rollback of data
}

module "postgres" {
  source = "../../modules/managed-postgres"

  service_name      = var.service_name
  environment       = "prod"
  region            = "GRA"
  plan              = "business"
  flavor            = "db1-15"      # production-grade flavor
  postgres_version  = "15"
  allowed_ip_ranges = var.allowed_ip_ranges
}