terraform {
  required_providers {
    ovh = {
      source  = "ovh/ovh"
      version = "~> 2.1"
    }
  }
}

# ============================================================
# PRIVATE NETWORK
# Same region variable used everywhere — confirmed by OVH tests
# ============================================================

resource "ovh_cloud_project_network_private" "main" {
  service_name = var.service_name
  name         = "${var.cluster_name}-${var.environment}-network"
  regions      = [var.region]
  vlan_id      = var.environment == "prod" ? 100 : 200
}

resource "ovh_cloud_project_network_private_subnet" "main" {
  service_name = var.service_name
  network_id   = ovh_cloud_project_network_private.main.id
  region       = var.region
  start        = "10.0.0.2"
  end          = "10.0.255.254"
  network      = "10.0.0.0/16"
  dhcp         = true
  no_gateway   = false
}

# ============================================================
# KUBERNETES CLUSTER
# private_network_id uses openstackid — confirmed by OVH tests
# nodes_subnet_id uses subnet .id directly
# ============================================================

resource "ovh_cloud_project_kube" "main" {
  service_name = var.service_name
  name         = "${var.cluster_name}-${var.environment}"
  region       = var.region
  version      = var.kubernetes_version

  # Official pattern from OVH provider tests
  private_network_id = tolist(ovh_cloud_project_network_private.main.regions_attributes[*].openstackid)[0]
  nodes_subnet_id    = ovh_cloud_project_network_private_subnet.main.id

  private_network_configuration {
    default_vrack_gateway              = ""
    private_network_routing_as_default = false
  }

  update_policy = "ALWAYS_UPDATE"
}

# ============================================================
# NODE POOL
# ============================================================

resource "ovh_cloud_project_kube_nodepool" "main" {
  service_name  = var.service_name
  kube_id       = ovh_cloud_project_kube.main.id
  name          = "main-pool"
  flavor_name   = var.node_flavor
  desired_nodes = var.node_count
  min_nodes     = var.environment == "prod" ? var.node_count : 1
  max_nodes     = var.environment == "prod" ? var.node_count * 2 : var.node_count
  autoscale     = var.environment == "prod" ? true : false
}