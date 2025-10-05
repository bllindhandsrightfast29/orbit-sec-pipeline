# Terraform IaC Security Demo

This directory contains **intentionally insecure** Terraform configurations for demonstrating IaC security scanning.

## ⚠️ Security Issues (Intentional)

### S3 Bucket
- ❌ No versioning enabled
- ❌ No encryption at rest
- ❌ Public access not blocked

### Security Group
- ❌ SSH (port 22) open to 0.0.0.0/0
- ❌ HTTP instead of HTTPS
- ❌ Overly permissive outbound rules

### EC2 Instance
- ❌ No EBS encryption
- ❌ Public IP assigned
- ❌ No IMDSv2 enforcement

### RDS Database
- ❌ Hardcoded password: "changeme123"
- ❌ Publicly accessible
- ❌ No encryption at rest
- ❌ No backup retention
- ❌ Deletion protection disabled

### IAM Role
- ❌ AdministratorAccess policy attached (too permissive)

### CloudWatch Logs
- ❌ No KMS encryption
- ❌ Short retention period (1 day)

## Detection

These issues are detected by:
- **Trivy**: Config scanning for Terraform
- **Checkov**: Policy-as-code validation
- **GitHub Actions**: Automated scanning in CI/CD

## Usage

**DO NOT DEPLOY THIS TO AWS!** This is for testing security scanners only.

To test locally:
```bash
# Scan with Trivy
trivy config terraform/ --severity CRITICAL,HIGH,MEDIUM

# Scan with Checkov (if installed)
checkov -d terraform/ --framework terraform
```

## Remediation Guide

See `docs/architecture.md` for how to fix these issues in a real infrastructure deployment.
