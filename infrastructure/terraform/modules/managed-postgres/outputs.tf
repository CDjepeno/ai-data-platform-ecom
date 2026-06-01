
output "postgres_host" {
  description = "Hostname to use in your DATABASE_URL"
  value       = ovh_cloud_project_database.postgres.endpoints[0].domain
  sensitive   = true
}

output "postgres_port" {
  value = ovh_cloud_project_database.postgres.endpoints[0].port
}

output "postgres_user" {
  value = ovh_cloud_project_database_postgresql_user.app_user.name
}

output "postgres_password" {
  value     = ovh_cloud_project_database_postgresql_user.app_user.password
  sensitive = true
}

output "connection_string" {
  description = "Full DATABASE_URL — inject this as a K8s secret"
  value = format(
    "postgresql://%s:%s@%s:%s/ecom",
    ovh_cloud_project_database_postgresql_user.app_user.name,
    ovh_cloud_project_database_postgresql_user.app_user.password,
    ovh_cloud_project_database.postgres.endpoints[0].domain,
    ovh_cloud_project_database.postgres.endpoints[0].port
  )
  sensitive = true
}