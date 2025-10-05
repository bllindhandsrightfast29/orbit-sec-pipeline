"""
Artifact Parser for ORBIT-SEC Dashboard
Parses real GitHub Actions security scan artifacts
"""
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


def parse_trivy_sarif(file_path: Path) -> Dict[str, Any]:
    """Parse Trivy SARIF format report"""
    if not file_path.exists():
        return {"critical": 0, "high": 0, "medium": 0, "low": 0, "findings": []}

    with open(file_path) as f:
        sarif_data = json.load(f)

    findings = []
    severity_count = {"critical": 0, "high": 0, "medium": 0, "low": 0}

    # Parse SARIF results
    for run in sarif_data.get("runs", []):
        for result in run.get("results", []):
            severity = result.get("level", "none").lower()
            if severity == "error":
                severity = "high"
            elif severity == "warning":
                severity = "medium"
            elif severity == "note":
                severity = "low"

            # Extract CVE from ruleId
            rule_id = result.get("ruleId", "")
            message = result.get("message", {}).get("text", "No description")

            # Get location info
            locations = result.get("locations", [])
            package = ""
            if locations:
                uri = locations[0].get("physicalLocation", {}).get("artifactLocation", {}).get("uri", "")
                package = uri

            severity_count[severity] = severity_count.get(severity, 0) + 1

            findings.append({
                "severity": severity.upper(),
                "cve": rule_id,
                "package": package,
                "description": message,
                "fixed_version": "See report for details"
            })

    return {
        "critical": severity_count.get("critical", 0),
        "high": severity_count.get("high", 0),
        "medium": severity_count.get("medium", 0),
        "low": severity_count.get("low", 0),
        "findings": findings[:5]  # Top 5 findings
    }


def parse_gitleaks_json(file_path: Path) -> Dict[str, Any]:
    """Parse Gitleaks JSON report"""
    if not file_path.exists():
        return {"critical": 0, "findings": []}

    with open(file_path) as f:
        data = json.load(f)

    findings = []
    for leak in data:
        findings.append({
            "severity": "CRITICAL",
            "type": leak.get("Description", "Secret Detected"),
            "file": leak.get("File", "unknown"),
            "line": leak.get("StartLine", 0),
            "description": f"{leak.get('Match', 'Secret')} detected"
        })

    return {
        "critical": len(findings),
        "findings": findings[:5]
    }


def parse_trivy_table(file_path: Path) -> Dict[str, Any]:
    """Parse Trivy table format output"""
    if not file_path.exists():
        return {"critical": 0, "high": 0, "medium": 0, "low": 0, "findings": []}

    # For table format, we'll do basic text parsing
    # This is a simplified version - SARIF is preferred
    findings = []
    severity_count = {"critical": 0, "high": 0, "medium": 0, "low": 0}

    with open(file_path) as f:
        content = f.read()

    # Count severity mentions (rough approximation)
    severity_count["critical"] = content.lower().count("critical")
    severity_count["high"] = content.lower().count("high")
    severity_count["medium"] = content.lower().count("medium")
    severity_count["low"] = content.lower().count("low")

    return {
        "critical": severity_count["critical"],
        "high": severity_count["high"],
        "medium": severity_count["medium"],
        "low": severity_count["low"],
        "findings": findings
    }


def load_real_artifacts(artifacts_dir: str = "../artifacts") -> Dict[str, Any]:
    """Load and parse all real artifacts"""
    artifacts_path = Path(artifacts_dir)

    if not artifacts_path.exists():
        return None  # Will use mock data

    result = {
        "timestamp": datetime.now().isoformat(),
        "pipeline_status": "UNKNOWN",
        "scans": {}
    }

    # Parse dependency scan
    trivy_report = artifacts_path / "trivy-report.sarif"
    if trivy_report.exists():
        dep_data = parse_trivy_sarif(trivy_report)
        result["scans"]["dependencies"] = {
            "name": "Dependency Scan (Trivy)",
            "status": "FAILED" if dep_data["critical"] > 0 or dep_data["high"] > 0 else "PASSED",
            **dep_data
        }

    # Parse secret scan
    gitleaks_report = artifacts_path / "gitleaks-report.json"
    if gitleaks_report.exists():
        secret_data = parse_gitleaks_json(gitleaks_report)
        result["scans"]["secrets"] = {
            "name": "Secret Detection (Gitleaks)",
            "status": "DETECTED" if secret_data["critical"] > 0 else "PASSED",
            "high": 0,
            "medium": 0,
            "low": 0,
            **secret_data
        }

    # Parse container scan
    trivy_image = artifacts_path / "trivy-image-results.txt"
    if trivy_image.exists():
        img_data = parse_trivy_table(trivy_image)
        result["scans"]["container"] = {
            "name": "Container Image Scan (Trivy)",
            "status": "FAILED" if img_data["critical"] > 0 or img_data["high"] > 0 else "PASSED",
            **img_data
        }

    # Parse IaC scans
    trivy_terraform = artifacts_path / "trivy-iac-terraform.txt"
    if trivy_terraform.exists():
        tf_data = parse_trivy_table(trivy_terraform)
        result["scans"]["iac_terraform"] = {
            "name": "IaC Scan - Terraform",
            "status": "FAILED" if tf_data["critical"] > 0 or tf_data["high"] > 0 else "PASSED",
            **tf_data
        }

    trivy_k8s = artifacts_path / "trivy-iac-k8s.txt"
    if trivy_k8s.exists():
        k8s_data = parse_trivy_table(trivy_k8s)
        result["scans"]["iac_kubernetes"] = {
            "name": "IaC Scan - Kubernetes",
            "status": "FAILED" if k8s_data["critical"] > 0 or k8s_data["high"] > 0 else "PASSED",
            **k8s_data
        }

    # Calculate totals
    total_vulns = sum(
        scan.get("critical", 0) + scan.get("high", 0) + scan.get("medium", 0) + scan.get("low", 0)
        for scan in result["scans"].values()
    )

    result["total_vulnerabilities"] = total_vulns
    result["critical_count"] = sum(scan.get("critical", 0) for scan in result["scans"].values())
    result["high_count"] = sum(scan.get("high", 0) for scan in result["scans"].values())
    result["medium_count"] = sum(scan.get("medium", 0) for scan in result["scans"].values())
    result["low_count"] = sum(scan.get("low", 0) for scan in result["scans"].values())

    # Determine overall status
    if result["critical_count"] > 0 or result["high_count"] > 0:
        result["pipeline_status"] = "FAILED"
    else:
        result["pipeline_status"] = "PASSED"

    return result


if __name__ == "__main__":
    # Test parser
    data = load_real_artifacts()
    if data:
        print(json.dumps(data, indent=2))
    else:
        print("No artifacts found. Run GitHub Actions pipeline first or use mock data.")
