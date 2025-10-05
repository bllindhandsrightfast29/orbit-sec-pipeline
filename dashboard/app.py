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
    c.execute("""SELECT id, scan_type, severity, package, vulnerability, description, file, line, installed_version, fixed_version
                 FROM vulnerabilities WHERE scan_id = ?""", (scan_id,))
    vulns = c.fetchall()

    conn.close()

    # Organize by scan type
    dependency_vulns = [v for v in vulns if v[1] == "dependency"]
    secret_vulns = [v for v in vulns if v[1] == "secret"]

    # Count by severity
    def count_severity(vuln_list):
        critical = sum(1 for v in vuln_list if v[2] == "CRITICAL")
        high = sum(1 for v in vuln_list if v[2] == "HIGH")
        medium = sum(1 for v in vuln_list if v[2] == "MEDIUM")
        low = sum(1 for v in vuln_list if v[2] == "LOW")
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
                        "id": v[0],
                        "severity": v[2],
                        "cve": v[4],
                        "package": v[3],
                        "description": v[5],
                        "file": v[6],
                        "line": v[7],
                        "installed_version": v[8] if len(v) > 8 else "",
                        "fixed_version": v[9] if len(v) > 9 else ""
                    } for v in dependency_vulns  # Show ALL findings
                ]
            },
            "secrets": {
                "name": "Secret Detection (Gitleaks)",
                "status": "DETECTED" if secret_counts["total"] > 0 else "PASSED",
                **secret_counts,
                "findings": [
                    {
                        "id": v[0],
                        "severity": v[2],
                        "type": v[3],
                        "description": v[5],
                        "file": v[6],
                        "line": v[7]
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

@app.post("/api/fix/{vuln_id}")
async def fix_vulnerability(vuln_id: int):
    """Fix a single vulnerability by updating requirements file"""
    if not DB_PATH.exists():
        return {"error": "No scan database found"}

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Get vulnerability details
    c.execute("""SELECT package, fixed_version, file, installed_version
                 FROM vulnerabilities WHERE id = ?""", (vuln_id,))
    vuln = c.fetchone()
    conn.close()

    if not vuln:
        return {"error": "Vulnerability not found"}

    package, fixed_version, file_path, installed_version = vuln

    if not fixed_version:
        return {"error": "No fix version available"}

    # Update requirements file
    try:
        target_file = Path(__file__).parent.parent / file_path
        if not target_file.exists():
            return {"error": f"File not found: {file_path}"}

        # Backup original
        backup_path = target_file.with_suffix('.txt.backup')

        # Read current content
        with open(target_file, 'r') as f:
            content = f.read()

        # Save backup
        with open(backup_path, 'w') as f:
            f.write(content)

        # Replace version
        if installed_version:
            old_line = f"{package}=={installed_version}"
            new_line = f"{package}=={fixed_version}"
        else:
            # Fallback: find any line with the package
            import re
            pattern = rf'^{re.escape(package)}==.*$'
            new_line = f"{package}=={fixed_version}"
            content = re.sub(pattern, new_line, content, flags=re.MULTILINE)

        if installed_version and old_line in content:
            updated_content = content.replace(old_line, new_line)
        else:
            updated_content = content

        with open(target_file, 'w') as f:
            f.write(updated_content)

        return {
            "success": True,
            "package": package,
            "old_version": installed_version,
            "new_version": fixed_version,
            "file": file_path,
            "backup": str(backup_path.name)
        }
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/fix-all")
async def fix_all_vulnerabilities():
    """Fix all vulnerabilities with available fixes"""
    if not DB_PATH.exists():
        return {"error": "No scan database found"}

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Get all fixable vulnerabilities
    c.execute("""SELECT id, package, fixed_version, file, installed_version
                 FROM vulnerabilities
                 WHERE fixed_version != '' AND fixed_version IS NOT NULL
                 AND file LIKE '%requirements.txt%'""")
    vulns = c.fetchall()
    conn.close()

    if not vulns:
        return {"error": "No fixable vulnerabilities found"}

    # Group by file
    files_to_fix = {}
    for vuln_id, package, fixed_version, file_path, installed_version in vulns:
        if file_path not in files_to_fix:
            files_to_fix[file_path] = []
        files_to_fix[file_path].append({
            'package': package,
            'installed': installed_version,
            'fixed': fixed_version
        })

    fixed_count = 0
    results = []

    for file_path, fixes in files_to_fix.items():
        try:
            target_file = Path(__file__).parent.parent / file_path
            if not target_file.exists():
                continue

            # Read and backup
            with open(target_file, 'r') as f:
                content = f.read()

            backup_path = target_file.with_suffix('.txt.backup')
            with open(backup_path, 'w') as f:
                f.write(content)

            # Apply all fixes
            updated_content = content
            for fix in fixes:
                if fix['installed']:
                    old_line = f"{fix['package']}=={fix['installed']}"
                    new_line = f"{fix['package']}=={fix['fixed']}"
                    updated_content = updated_content.replace(old_line, new_line)
                    fixed_count += 1

            # Write updated file
            with open(target_file, 'w') as f:
                f.write(updated_content)

            results.append({
                "file": file_path,
                "fixes_applied": len(fixes),
                "backup": str(backup_path.name)
            })
        except Exception as e:
            results.append({
                "file": file_path,
                "error": str(e)
            })

    return {
        "success": True,
        "total_fixed": fixed_count,
        "files_updated": results
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
