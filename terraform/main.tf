# ORBIT-SEC Terraform Demo Configuration
# Intentionally includes misconfigurations for IaC scanning demonstration

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# S3 Bucket with intentional security issues
resource "aws_s3_bucket" "app_data" {
  bucket = "orbit-sec-app-data-${var.environment}"

  # VULNERABILITY: No versioning enabled
  # VULNERABILITY: No encryption at rest

  tags = {
    Name        = "ORBIT-SEC Application Data"
    Environment = var.environment
    Project     = "DevSecOps Pipeline Demo"
  }
}

# VULNERABILITY: Public access not blocked
resource "aws_s3_bucket_public_access_block" "app_data" {
  bucket = aws_s3_bucket.app_data.id

  block_public_acls       = false  # Should be true
  block_public_policy     = false  # Should be true
  ignore_public_acls      = false  # Should be true
  restrict_public_buckets = false  # Should be true
}

# Security Group with overly permissive rules
resource "aws_security_group" "app_sg" {
  name        = "orbit-sec-app-sg"
  description = "Security group for ORBIT-SEC application"
  vpc_id      = var.vpc_id

  # VULNERABILITY: SSH open to the world
  ingress {
    description = "SSH from anywhere"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Should be restricted
  }

  # VULNERABILITY: HTTP instead of HTTPS
  ingress {
    description = "HTTP from anywhere"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # VULNERABILITY: All outbound traffic allowed
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "orbit-sec-sg"
  }
}

# EC2 Instance with security issues
resource "aws_instance" "app_server" {
  ami           = var.ami_id
  instance_type = "t2.micro"

  vpc_security_group_ids = [aws_security_group.app_sg.id]

  # VULNERABILITY: No encryption for EBS volumes
  # VULNERABILITY: No monitoring enabled
  # VULNERABILITY: Public IP assigned
  associate_public_ip_address = true

  # VULNERABILITY: No IMDSv2 enforcement
  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "optional"  # Should be "required" for IMDSv2
  }

  tags = {
    Name = "orbit-sec-app-server"
  }
}

# RDS Instance with security issues
resource "aws_db_instance" "app_database" {
  identifier     = "orbit-sec-db"
  engine         = "postgres"
  engine_version = "13.7"
  instance_class = "db.t3.micro"

  allocated_storage = 20

  db_name  = "orbitdb"
  username = "admin"
  password = "changeme123"  # VULNERABILITY: Hardcoded password

  # VULNERABILITY: Publicly accessible
  publicly_accessible = true

  # VULNERABILITY: No encryption at rest
  storage_encrypted = false

  # VULNERABILITY: No backup retention
  backup_retention_period = 0

  # VULNERABILITY: Deletion protection disabled
  deletion_protection = false

  skip_final_snapshot = true

  tags = {
    Name = "orbit-sec-database"
  }
}

# IAM Role with overly permissive policies
resource "aws_iam_role" "app_role" {
  name = "orbit-sec-app-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

# VULNERABILITY: Admin access granted
resource "aws_iam_role_policy_attachment" "admin_policy" {
  role       = aws_iam_role.app_role.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"  # Too permissive
}

# CloudWatch Log Group without encryption
resource "aws_cloudwatch_log_group" "app_logs" {
  name = "/aws/orbit-sec/app"

  # VULNERABILITY: No KMS encryption
  # VULNERABILITY: Short retention period
  retention_in_days = 1  # Should be longer

  tags = {
    Name = "orbit-sec-logs"
  }
}
