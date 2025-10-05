# Kubernetes Security Demo

This directory contains **intentionally insecure** Kubernetes manifests for demonstrating K8s security scanning.

## ⚠️ Security Issues (Intentional)

### Deployment Security Issues

#### Container Configuration
- ❌ Running as root (no runAsNonRoot)
- ❌ Privileged container enabled
- ❌ AllowPrivilegeEscalation: true
- ❌ All capabilities added (CAP_ALL)
- ❌ ReadOnlyRootFilesystem: false

#### Secrets Management
- ❌ Hardcoded DATABASE_PASSWORD in env vars
- ❌ Hardcoded API_KEY in env vars
- ❌ No Kubernetes Secrets usage

#### Resource Management
- ❌ No CPU/memory limits defined
- ❌ No CPU/memory requests defined
- ❌ No liveness probes
- ❌ No readiness probes

#### Host Access
- ❌ hostNetwork: true
- ❌ hostPID: true
- ❌ hostIPC: true
- ❌ hostPath volume mounted to root (/)

#### Image Security
- ❌ imagePullPolicy: IfNotPresent (not Always)
- ❌ No image pull secrets

### Service Security Issues
- ❌ Type: LoadBalancer (publicly exposed)
- ❌ No TLS/HTTPS configuration
- ❌ No network policies

## Detection

These issues are detected by:
- **Trivy**: Config scanning for Kubernetes
- **Checkov**: Pod Security Policy validation
- **GitHub Actions**: Automated scanning in CI/CD

## Usage

**DO NOT DEPLOY THIS TO A CLUSTER!** This is for testing security scanners only.

To test locally:
```bash
# Scan with Trivy
trivy config kubernetes/ --severity CRITICAL,HIGH,MEDIUM

# Scan with Checkov (if installed)
checkov -d kubernetes/ --framework kubernetes
```

## Secure Configuration Example

A properly secured deployment should have:
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 10000
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop:
    - ALL
```

And use Kubernetes Secrets:
```yaml
env:
- name: DATABASE_PASSWORD
  valueFrom:
    secretKeyRef:
      name: app-secrets
      key: db-password
```

## Remediation Guide

See `docs/architecture.md` for comprehensive security best practices.
