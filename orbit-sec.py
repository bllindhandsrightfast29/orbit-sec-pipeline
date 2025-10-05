#!/usr/bin/env python3
"""
ORBIT-SEC - Standalone Security Scanner
Scans any project for vulnerabilities and launches dashboard
"""
import sys
import subprocess
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import webbrowser
import time

class Scanner:
    def __init__(self, target_path):
        self.target = Path(target_path).resolve()
        self.db_path = Path(__file__).parent / "results.db"
        self.setup_database()

    def setup_database(self):
        """Create SQLite database for storing scan results"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS scans
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      target TEXT,
                      timestamp TEXT,
                      status TEXT)''')

        c.execute('''CREATE TABLE IF NOT EXISTS vulnerabilities
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      scan_id INTEGER,
                      scan_type TEXT,
                      severity TEXT,
                      package TEXT,
                      vulnerability TEXT,
                      description TEXT,
                      file TEXT,
                      line INTEGER,
                      installed_version TEXT,
                      fixed_version TEXT,
                      FOREIGN KEY(scan_id) REFERENCES scans(id))''')

        conn.commit()
        conn.close()

    def check_dependencies(self):
        """Verify Trivy and Gitleaks are installed"""
        print("Checking dependencies...")

        missing = []

        if subprocess.run(["which", "trivy"], capture_output=True).returncode != 0:
            missing.append("trivy")

        if subprocess.run(["which", "gitleaks"], capture_output=True).returncode != 0:
            missing.append("gitleaks")

        if missing:
            print(f"\nMissing tools: {', '.join(missing)}")
            print("\nInstall with:")
            if "trivy" in missing:
                print("  brew install trivy")
            if "gitleaks" in missing:
                print("  brew install gitleaks")
            sys.exit(1)

        print("✓ Dependencies OK")

    def run_trivy(self):
        """Run Trivy filesystem scan"""
        print(f"\nRunning Trivy scan on {self.target}...")

        try:
            result = subprocess.run(
                ["trivy", "fs", "--format", "json", "--severity", "CRITICAL,HIGH,MEDIUM,LOW", str(self.target)],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode not in [0, 1]:  # 1 means vulnerabilities found
                print(f"Warning: Trivy exited with code {result.returncode}")

            data = json.loads(result.stdout) if result.stdout else {"Results": []}

            vulnerabilities = []
            for res in data.get("Results", []):
                for vuln in res.get("Vulnerabilities", []):
                    # Extract fix version
                    fixed_version = vuln.get("FixedVersion", "")
                    installed_version = vuln.get("InstalledVersion", "")

                    vulnerabilities.append({
                        "scan_type": "dependency",
                        "severity": vuln.get("Severity", "UNKNOWN"),
                        "package": vuln.get("PkgName", "unknown"),
                        "vulnerability": vuln.get("VulnerabilityID", ""),
                        "description": vuln.get("Title", ""),
                        "file": res.get("Target", ""),
                        "line": None,
                        "installed_version": installed_version,
                        "fixed_version": fixed_version
                    })

            print(f"✓ Trivy: Found {len(vulnerabilities)} vulnerabilities")
            return vulnerabilities

        except subprocess.TimeoutExpired:
            print("✗ Trivy scan timed out")
            return []
        except json.JSONDecodeError:
            print("✗ Could not parse Trivy output")
            return []
        except Exception as e:
            print(f"✗ Trivy error: {e}")
            return []

    def run_gitleaks(self):
        """Run Gitleaks secret scan"""
        print(f"\nRunning Gitleaks scan on {self.target}...")

        try:
            result = subprocess.run(
                ["gitleaks", "detect", "--source", str(self.target), "--report-format", "json", "--report-path", "/dev/stdout", "--no-git"],
                capture_output=True,
                text=True,
                timeout=60
            )

            # Gitleaks exits with 1 if secrets found, which is expected
            if result.stdout:
                data = json.loads(result.stdout)
            else:
                data = []

            vulnerabilities = []
            if isinstance(data, list):
                for secret in data:
                    vulnerabilities.append({
                        "scan_type": "secret",
                        "severity": "CRITICAL",
                        "package": secret.get("RuleID", ""),
                        "vulnerability": secret.get("Description", "Secret detected"),
                        "description": f"Secret found: {secret.get('Secret', '')[:20]}...",
                        "file": secret.get("File", ""),
                        "line": secret.get("StartLine", 0)
                    })

            print(f"✓ Gitleaks: Found {len(vulnerabilities)} secrets")
            return vulnerabilities

        except subprocess.TimeoutExpired:
            print("✗ Gitleaks scan timed out")
            return []
        except json.JSONDecodeError:
            print("✗ Could not parse Gitleaks output")
            return []
        except Exception as e:
            print(f"✗ Gitleaks error: {e}")
            return []

    def save_results(self, trivy_vulns, gitleaks_vulns):
        """Save scan results to database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Create scan record
        total_vulns = len(trivy_vulns) + len(gitleaks_vulns)
        status = "FAILED" if total_vulns > 0 else "PASSED"

        c.execute("INSERT INTO scans (target, timestamp, status) VALUES (?, ?, ?)",
                  (str(self.target), datetime.now().isoformat(), status))
        scan_id = c.lastrowid

        # Insert vulnerabilities
        all_vulns = trivy_vulns + gitleaks_vulns
        for vuln in all_vulns:
            c.execute("""INSERT INTO vulnerabilities
                        (scan_id, scan_type, severity, package, vulnerability, description, file, line, installed_version, fixed_version)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                     (scan_id, vuln["scan_type"], vuln["severity"], vuln["package"],
                      vuln["vulnerability"], vuln["description"], vuln["file"], vuln["line"],
                      vuln.get("installed_version", ""), vuln.get("fixed_version", "")))

        conn.commit()
        conn.close()

        return scan_id

    def scan(self):
        """Run complete scan"""
        if not self.target.exists():
            print(f"Error: {self.target} does not exist")
            sys.exit(1)

        print(f"\n{'='*60}")
        print(f"ORBIT-SEC Security Scan")
        print(f"Target: {self.target}")
        print(f"{'='*60}")

        self.check_dependencies()

        trivy_vulns = self.run_trivy()
        gitleaks_vulns = self.run_gitleaks()

        scan_id = self.save_results(trivy_vulns, gitleaks_vulns)

        total = len(trivy_vulns) + len(gitleaks_vulns)
        critical = sum(1 for v in trivy_vulns + gitleaks_vulns if v["severity"] == "CRITICAL")
        high = sum(1 for v in trivy_vulns + gitleaks_vulns if v["severity"] == "HIGH")

        print(f"\n{'='*60}")
        print(f"Scan Complete (ID: {scan_id})")
        print(f"Total Vulnerabilities: {total}")
        print(f"  Critical: {critical}")
        print(f"  High: {high}")
        print(f"{'='*60}")

        return scan_id

def main():
    if len(sys.argv) < 2:
        print("Usage: python orbit-sec.py <path-to-project>")
        print("\nExample:")
        print("  python orbit-sec.py ~/my-project")
        print("  python orbit-sec.py /path/to/VISUS")
        print("  python orbit-sec.py .")
        sys.exit(1)

    target = sys.argv[1]
    scanner = Scanner(target)
    scan_id = scanner.scan()

    print("\nLaunching dashboard...")
    print("Dashboard: http://localhost:8000")
    print("\nPress Ctrl+C to stop\n")

    # Launch dashboard
    dashboard_path = Path(__file__).parent / "dashboard" / "app.py"
    if dashboard_path.exists():
        try:
            time.sleep(2)
            webbrowser.open("http://localhost:8000")
            subprocess.run(["python3", str(dashboard_path)])
        except KeyboardInterrupt:
            print("\nShutting down...")
    else:
        print(f"Dashboard not found at {dashboard_path}")
        print("Creating dashboard launcher...")
        # Try alternate path
        alt_dashboard = Path(__file__).parent / "dashboard" / "dashboard.py"
        if alt_dashboard.exists():
            subprocess.run(["python3", str(alt_dashboard)])
        else:
            print("Run: cd dashboard && python dashboard.py")

if __name__ == "__main__":
    main()
