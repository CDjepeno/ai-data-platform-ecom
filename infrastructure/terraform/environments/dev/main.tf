terraform {
  required_version = ">= 1.9.0"

  required_providers {
    ovh = {
      source  = "ovh/ovh"
      version = "~> 2.1"
    }
  }

  backend "s3" {
    bucket = "ecom-terraform-state-dev"
    key    = "dev/terraform.tfstate"
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
  environment        = "dev"
  region             = "GRA9"
  kubernetes_version = "1.31"
  node_flavor        = "b3-8"
  node_count         = 1
  vlan_id            = 200

  tags = {
    project = var.project_name
    env     = "dev"
  }
}

module "warehouse_storage" {
  source = "../../modules/object-storage"

  service_name       = var.service_name
  bucket_name        = "${var.project_name}-warehouse"
  environment        = "dev"
  region             = "GRA"
  versioning_enabled = false
}

module "postgres" {
  source = "../../modules/managed-postgres"

  service_name      = var.service_name
  environment       = "dev"
  region            = "GRA"
  plan              = "essential"
  flavor            = "db1-4"
  postgres_version  = "15"
  allowed_ip_ranges = var.allowed_ip_ranges
}