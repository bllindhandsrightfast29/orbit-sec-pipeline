"""
ORBIT-SEC Security Dashboard
FastAPI backend for visualizing security scan results
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
import json
from pathlib import Path
from typing import Dict, List, Any
import random

app = FastAPI(title="ORBIT-SEC Dashboard", version="1.0.0")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Mock data for demo (replace with real artifact parsing later)
def generate_mock_scan_data() -> Dict[str, Any]:
    """Generate realistic mock data for dashboard demo"""
    return {
        "timestamp": datetime.now().isoformat(),
        "pipeline_status": "FAILED",  # Intentional due to vulnerabilities
        "total_vulnerabilities": 47,
        "critical_count": 12,
        "high_count": 18,
        "medium_count": 15,
        "low_count": 2,
        "scans": {
            "dependencies": {
                "name": "Dependency Scan (Trivy)",
                "status": "FAILED",
                "critical": 8,
                "high": 12,
                "medium": 7,
                "low": 1,
                "findings": [
                    {
                        "severity": "CRITICAL",
                        "cve": "CVE-2023-30861",
                        "package": "Flask==2.0.1",
                        "description": "HTTP request smuggling vulnerability",
                        "fixed_version": "2.3.2"
                    },
                    {
                        "severity": "CRITICAL",
                        "cve": "CVE-2023-32681",
                        "package": "requests==2.25.1",
                        "description": "Proxy-Authorization header leak",
                        "fixed_version": "2.31.0"
                    },
                    {
                        "severity": "HIGH",
                        "cve": "CVE-2023-25577",
                        "package": "Werkzeug==2.0.1",
                        "description": "Cookie parsing vulnerability",
                        "fixed_version": "2.3.3"
                    },
                    {
                        "severity": "CRITICAL",
                        "cve": "CVE-2020-28493",
                        "package": "Jinja2==2.11.3",
                        "description": "ReDoS vulnerability in urlize filter",
                        "fixed_version": "2.11.4"
                    }
                ]
            },
            "secrets": {
                "name": "Secret Detection (Gitleaks)",
                "status": "DETECTED",
                "critical": 2,
                "high": 0,
                "medium": 0,
                "low": 0,
                "findings": [
                    {
                        "severity": "CRITICAL",
                        "type": "Stripe API Key",
                        "file": "app.py",
                        "line": 12,
                        "description": "Hardcoded Stripe API key detected"
                    },
                    {
                        "severity": "CRITICAL",
                        "type": "Generic Password",
                        "file": "app.py",
                        "line": 13,
                        "description": "Hardcoded database password"
                    }
                ]
            },
            "container": {
                "name": "Container Image Scan (Trivy)",
                "status": "FAILED",
                "critical": 2,
                "high": 4,
                "medium": 6,
                "low": 1,
                "findings": [
                    {
                        "severity": "CRITICAL",
                        "cve": "CVE-2024-1234",
                        "package": "libssl1.1",
                        "description": "OpenSSL vulnerability in base image",
                        "fixed_version": "1.1.1w-r11"
                    },
                    {
                        "severity": "HIGH",
                        "cve": "CVE-2024-5678",
                        "package": "apt",
                        "description": "Package manager vulnerability",
                        "fixed_version": "2.0.9"
                    }
                ]
            },
            "iac_terraform": {
                "name": "IaC Scan - Terraform",
                "status": "FAILED",
                "critical": 0,
                "high": 2,
                "medium": 2,
                "low": 0,
                "findings": [
                    {
                        "severity": "HIGH",
                        "issue": "S3 Bucket Public Access",
                        "resource": "aws_s3_bucket.app_data",
                        "description": "S3 bucket allows public access",
                        "remediation": "Enable block_public_acls and block_public_policy"
                    },
                    {
                        "severity": "HIGH",
                        "issue": "Hardcoded RDS Password",
                        "resource": "aws_db_instance.app_database",
                        "description": "Database password is hardcoded",
                        "remediation": "Use AWS Secrets Manager or environment variables"
                    },
                    {
                        "severity": "MEDIUM",
                        "issue": "Security Group Port 22 Open",
                        "resource": "aws_security_group.app_sg",
                        "description": "SSH port open to 0.0.0.0/0",
                        "remediation": "Restrict SSH access to specific IPs"
                    }
                ]
            },
            "iac_kubernetes": {
                "name": "IaC Scan - Kubernetes",
                "status": "FAILED",
                "critical": 0,
                "high": 3,
                "medium": 0,
                "low": 0,
                "findings": [
                    {
                        "severity": "HIGH",
                        "issue": "Privileged Container",
                        "resource": "deployment.yaml",
                        "description": "Container running with privileged: true",
                        "remediation": "Set privileged: false and drop capabilities"
                    },
                    {
                        "severity": "HIGH",
                        "issue": "Hardcoded Secrets in Env",
                        "resource": "deployment.yaml",
                        "description": "Database password in environment variables",
                        "remediation": "Use Kubernetes Secrets"
                    },
                    {
                        "severity": "HIGH",
                        "issue": "hostPath Volume Mount",
                        "resource": "deployment.yaml",
                        "description": "hostPath volume mounted to /",
                        "remediation": "Avoid hostPath or use specific paths with readOnly"
                    }
                ]
            }
        }
    }


def parse_real_artifacts() -> Dict[str, Any]:
    """Parse real GitHub Actions artifacts when available"""
    try:
        from artifact_parser import load_real_artifacts

        # Try to load real artifacts first
        real_data = load_real_artifacts("./artifacts")
        if real_data:
            return real_data
    except Exception as e:
        print(f"Could not load real artifacts: {e}")

    # Fallback to mock data for demo
    return generate_mock_scan_data()


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Render main dashboard"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/scans")
async def get_scans():
    """Get all scan results"""
    return parse_real_artifacts()


@app.get("/api/summary")
async def get_summary():
    """Get executive summary"""
    data = parse_real_artifacts()
    return {
        "status": data["pipeline_status"],
        "total_vulnerabilities": data["total_vulnerabilities"],
        "critical": data["critical_count"],
        "high": data["high_count"],
        "medium": data["medium_count"],
        "low": data["low_count"],
        "scan_types": len(data["scans"]),
        "timestamp": data["timestamp"]
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ORBIT-SEC Dashboard",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/timeline")
async def get_scan_timeline():
    """Get historical scan results (mock data for now)"""
    now = datetime.now()
    timeline = []

    for i in range(10, 0, -1):
        timestamp = now - timedelta(hours=i)
        # Simulate vulnerability reduction over time
        vuln_count = 47 - (10 - i) * 3
        timeline.append({
            "timestamp": timestamp.isoformat(),
            "total_vulnerabilities": max(vuln_count, 5),
            "critical": max(12 - (10 - i), 0),
            "high": max(18 - (10 - i), 2),
            "status": "FAILED" if vuln_count > 10 else "PASSED"
        })

    return timeline


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting ORBIT-SEC Dashboard...")
    print("📊 Dashboard: http://localhost:8000")
    print("📡 API Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
