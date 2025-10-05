# Terraform Outputs

output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.app_data.id
}

output "ec2_public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.app_server.public_ip
  sensitive   = false  # VULNERABILITY: Exposing IP in outputs
}

output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.app_database.endpoint
}

output "database_password" {
  description = "Database password"
  value       = aws_db_instance.app_database.password
  sensitive   = false  # VULNERABILITY: Password not marked sensitive
}
