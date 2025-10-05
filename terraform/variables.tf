# Terraform Variables for ORBIT-SEC Demo

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "vpc_id" {
  description = "VPC ID for security group"
  type        = string
  default     = "vpc-12345678"  # Placeholder - would be from data source in real scenario
}

variable "ami_id" {
  description = "AMI ID for EC2 instance"
  type        = string
  default     = "ami-0c55b159cbfafe1f0"  # Amazon Linux 2 example
}

variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to access the application"
  type        = list(string)
  default     = ["0.0.0.0/0"]  # VULNERABILITY: Too permissive
}
