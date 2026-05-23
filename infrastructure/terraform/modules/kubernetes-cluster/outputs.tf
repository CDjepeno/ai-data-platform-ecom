
output "cluster_id" {
  description = "OVHCloud cluster ID"
  value       = ovh_cloud_project_kube.main.id
}

output "kubeconfig" {
  description = "Kubeconfig to connect kubectl to this cluster"
  value       = ovh_cloud_project_kube.main.kubeconfig
  sensitive   = true
}

output "cluster_version" {
  description = "Actual Kubernetes version deployed"
  value       = ovh_cloud_project_kube.main.version
}

output "private_network_id" {
  description = "vRack private network ID — used by managed Postgres"
  value       = ovh_cloud_project_network_private.main.id
}