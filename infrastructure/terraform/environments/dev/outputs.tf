
output "kubeconfig" {
  description = "Run: terraform output -raw kubeconfig > ~/.kube/config"
  value       = module.kubernetes.kubeconfig
  sensitive   = true
}

output "warehouse_endpoint" {
  description = "S3 endpoint — replace http://minio:9000 in your Nessie config"
  value       = module.warehouse_storage.bucket_endpoint
}

output "warehouse_bucket" {
  value = module.warehouse_storage.bucket_name
}

output "postgres_connection_string" {
  description = "Inject this into your K8s secret for DATABASE_URL"
  value       = module.postgres.connection_string
  sensitive   = true
}