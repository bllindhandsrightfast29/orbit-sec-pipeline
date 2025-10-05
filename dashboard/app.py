#!/usr/bin/env python3
"""
ORBIT-SEC Dashboard - Reads REAL scan results from SQLite
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import sqlite3
from datetime import datetime

app = FastAPI(title="ORBIT-SEC Dashboard", version="1.0.0")

# Setup templates
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

DB_PATH = Path(__file__).parent.parent / "results.db"

def get_latest_scan():
    """Get most recent scan from database"""
    if not DB_PATH.exists():
        return None

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Get latest scan
    c.execute("SELECT id, target, timestamp, status FROM scans ORDER BY id DESC LIMIT 1")
    scan = c.fetchone()

    if not scan:
        conn.close()
        return None

    scan_id, target, timestamp, status = scan

    # Get vulnerabilities for this scan
    c.execute("""SELECT scan_type, severity, package, vulnerability, description, file, line
                 FROM vulnerabilities WHERE scan_id = ?""", (scan_id,))
    vulns = c.fetchall()

    conn.close()

    # Organize by scan type
    dependency_vulns = [v for v in vulns if v[0] == "dependency"]
    secret_vulns = [v for v in vulns if v[0] == "secret"]

    # Count by severity
    def count_severity(vuln_list):
        critical = sum(1 for v in vuln_list if v[1] == "CRITICAL")
        high = sum(1 for v in vuln_list if v[1] == "HIGH")
        medium = sum(1 for v in vuln_list if v[1] == "MEDIUM")
        low = sum(1 for v in vuln_list if v[1] == "LOW")
        return {"critical": critical, "high": high, "medium": medium, "low": low, "total": len(vuln_list)}

    dep_counts = count_severity(dependency_vulns)
    secret_counts = count_severity(secret_vulns)

    return {
        "scan_id": scan_id,
        "target": target,
        "timestamp": timestamp,
        "status": status,
        "total_vulnerabilities": dep_counts["total"] + secret_counts["total"],
        "critical_count": dep_counts["critical"] + secret_counts["critical"],
        "high_count": dep_counts["high"] + secret_counts["high"],
        "medium_count": dep_counts["medium"] + secret_counts["medium"],
        "low_count": dep_counts["low"] + secret_counts["low"],
        "scans": {
            "dependencies": {
                "name": "Dependency Scan (Trivy)",
                "status": "FAILED" if dep_counts["total"] > 0 else "PASSED",
                **dep_counts,
                "findings": [
                    {
                        "severity": v[1],
                        "cve": v[3],
                        "package": v[2],
                        "description": v[4],
                        "file": v[5],
                        "line": v[6]
                    } for v in dependency_vulns  # Show ALL findings
                ]
            },
            "secrets": {
                "name": "Secret Detection (Gitleaks)",
                "status": "DETECTED" if secret_counts["total"] > 0 else "PASSED",
                **secret_counts,
                "findings": [
                    {
                        "severity": v[1],
                        "type": v[2],
                        "description": v[4],
                        "file": v[5],
                        "line": v[6]
                    } for v in secret_vulns  # Show ALL findings
                ]
            }
        }
    }

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Serve dashboard HTML"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/scans")
async def get_scans():
    """Get latest scan results"""
    scan_data = get_latest_scan()

    if not scan_data:
        return {
            "error": "No scans found",
            "message": "Run: python orbit-sec.py /path/to/project",
            "pipeline_status": "NO_DATA",
            "total_vulnerabilities": 0,
            "scans": {}
        }

    return scan_data

@app.get("/api/summary")
async def get_summary():
    """Get vulnerability summary"""
    scan_data = get_latest_scan()

    if not scan_data:
        return {
            "error": "No scans found",
            "status": "NO_DATA",
            "total_vulnerabilities": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }

    return {
        "status": scan_data["status"],
        "total_vulnerabilities": scan_data["total_vulnerabilities"],
        "critical": scan_data["critical_count"],
        "high": scan_data["high_count"],
        "medium": scan_data["medium_count"],
        "low": scan_data["low_count"],
        "scan_types": len(scan_data["scans"]),
        "timestamp": scan_data["timestamp"],
        "target": scan_data["target"]
    }

@app.get("/api/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "ORBIT-SEC Dashboard",
        "version": "1.0.0",
        "database": "connected" if DB_PATH.exists() else "not found",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting ORBIT-SEC Dashboard...")
    print("📊 Dashboard: http://localhost:8000")
    print("📡 API Docs: http://localhost:8000/docs")
    print("")
    if not DB_PATH.exists():
        print("⚠️  No scan results found!")
        print("   Run: python orbit-sec.py /path/to/project")
        print("")
    uvicorn.run(app, host="0.0.0.0", port=8000)
