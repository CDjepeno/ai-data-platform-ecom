output "bucket_name" {
  value = ovh_cloud_project_storage.main.name
}

output "bucket_endpoint" {
  value = "https://s3.${lower(var.region)}.io.cloud.ovh.net"
}

output "access_key" {
  value     = ovh_cloud_project_user_s3_credential.main.access_key_id
  sensitive = true
}

output "secret_key" {
  value     = ovh_cloud_project_user_s3_credential.main.secret_access_key
  sensitive = true
}