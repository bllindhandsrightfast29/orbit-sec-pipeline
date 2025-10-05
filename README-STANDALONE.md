# ORBIT-SEC - Standalone Security Scanner

**One command to scan any project for vulnerabilities.**

## Quick Start

```bash
# 1. Install dependencies
brew install trivy gitleaks

# 2. Scan any project
python orbit-sec.py /path/to/your/project

# Dashboard opens automatically at http://localhost:8000
```

That's it.

## What It Does

- ✅ Scans dependencies for known CVEs (using Trivy)
- ✅ Detects hardcoded secrets (using Gitleaks)
- ✅ Stores results in local SQLite database
- ✅ Launches visual dashboard showing **real** findings
- ✅ Works on **any** Python, Node, Go, Java, or other project

## Example Usage

### Scan VISUS network scanner
```bash
python orbit-sec.py ~/VISUS
```

### Scan Android app
```bash
python orbit-sec.py ~/wyn-ston
```

### Scan this demo project (intentional vulnerabilities)
```bash
python orbit-sec.py .
```

## Requirements

### Scanner Dependencies
- **Python 3.9+**
- **Trivy** - `brew install trivy` or [install guide](https://aquasecurity.github.io/trivy/latest/getting-started/installation/)
- **Gitleaks** - `brew install gitleaks` or [install guide](https://github.com/gitleaks/gitleaks#installing)

### Dashboard Dependencies
```bash
pip install fastapi uvicorn jinja2
```

Or use the existing venv:
```bash
source venv/bin/activate
```

## How It Works

1. **Scans your code** with industry-standard tools (Trivy + Gitleaks)
2. **Parses results** into a local SQLite database (`results.db`)
3. **Launches dashboard** at http://localhost:8000
4. **Shows real vulnerabilities** from your actual code

**No fake data. No mock results. Real scans on real code.**

## Output Example

```
============================================================
ORBIT-SEC Security Scan
Target: /Users/you/my-project
============================================================
Checking dependencies...
✓ Dependencies OK

Running Trivy scan on /Users/you/my-project...
✓ Trivy: Found 12 vulnerabilities

Running Gitleaks scan on /Users/you/my-project...
✓ Gitleaks: Found 2 secrets

============================================================
Scan Complete (ID: 1)
Total Vulnerabilities: 14
  Critical: 2
  High: 10
============================================================

Launching dashboard...
Dashboard: http://localhost:8000
```

## Dashboard Features

### Real-Time Visualization
- 📊 Total vulnerability count
- 🔴 Critical/High/Medium/Low breakdown
- 📍 File paths and line numbers for each finding
- 📦 Package names and CVE IDs
- 🔐 Detected secrets (redacted)

### API Endpoints
- `GET /` - Dashboard UI
- `GET /api/scans` - Latest scan results (JSON)
- `GET /api/summary` - Executive summary
- `GET /api/health` - Health check
- `GET /docs` - Interactive API documentation

## Interview Demo

Perfect for technical interviews when they ask about security:

```bash
# 1. Scan their sandbox/codebase
python orbit-sec.py /path/to/their/code

# 2. Show dashboard with real findings
# 3. Explain each vulnerability type
# 4. Demonstrate remediation knowledge
# 5. Discuss security best practices
```

**This proves you can:**
- Use industry-standard security tools
- Parse and present complex data
- Build practical DevSecOps solutions
- Identify real vulnerabilities in real code

## GitHub Actions Integration (Optional)

Want automated scanning on every commit?

1. Copy the workflow to any project:
```bash
cp .github/workflows/security.yml /path/to/project/.github/workflows/
```

2. Push to GitHub - scans run automatically on every commit

3. View results in GitHub Actions tab

## Files & Architecture

```
orbit-sec-pipeline/
├── orbit-sec.py              # Main scanner (run this!)
├── results.db                # SQLite database (auto-created)
├── dashboard/
│   ├── app.py               # Dashboard backend (reads SQLite)
│   ├── templates/
│   │   └── index.html       # Dashboard UI
│   └── requirements.txt     # Dashboard dependencies
├── .github/workflows/
│   └── security.yml         # CI/CD integration (optional)
└── README-STANDALONE.md     # This file
```

## Database Schema

SQLite database stores:

**scans table:**
- `id` - Scan ID
- `target` - Path scanned
- `timestamp` - When scan ran
- `status` - PASSED or FAILED

**vulnerabilities table:**
- `scan_id` - Foreign key to scans
- `scan_type` - dependency or secret
- `severity` - CRITICAL/HIGH/MEDIUM/LOW
- `package` - Package name or secret type
- `vulnerability` - CVE ID or description
- `file` - File path
- `line` - Line number

## Advanced Usage

### Scan Multiple Projects
```bash
python orbit-sec.py ~/project1
python orbit-sec.py ~/project2
python orbit-sec.py ~/project3

# Dashboard shows latest scan
# Database keeps history of all scans
```

### Export Results
```bash
# Query database directly
sqlite3 results.db "SELECT * FROM vulnerabilities WHERE severity='CRITICAL'"

# Export to CSV
sqlite3 results.db -csv -header "SELECT * FROM vulnerabilities" > vulns.csv
```

### Automated Scanning
```bash
# Add to crontab for daily scans
0 9 * * * cd /path/to/orbit-sec && python orbit-sec.py /path/to/project
```

## Troubleshooting

### "Trivy not found"
```bash
brew install trivy
# or
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
```

### "Gitleaks not found"
```bash
brew install gitleaks
# or download from https://github.com/gitleaks/gitleaks/releases
```

### "Dashboard shows no data"
Make sure you ran the scanner first:
```bash
python orbit-sec.py .
```

### Port 8000 already in use
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9

# Or edit app.py to use different port
uvicorn.run(app, host="0.0.0.0", port=8001)
```

## Comparison: Mock vs Real

### Previous Version (Mock Data)
- ❌ Fake vulnerabilities for demo
- ❌ Hardcoded CVE numbers
- ❌ Can't scan real projects
- ✅ Pretty dashboard

### Current Version (Real Scanner)
- ✅ **Actual** Trivy + Gitleaks scans
- ✅ **Real** CVEs from real code
- ✅ Scans **any** project
- ✅ SQLite storage for history
- ✅ Same pretty dashboard + real data

## Project Status

- ✅ Standalone scanner (works anywhere)
- ✅ Real vulnerability detection
- ✅ SQLite storage
- ✅ Visual dashboard with real data
- ✅ GitHub Actions integration
- ⏭️ PDF report generation
- ⏭️ Multi-project comparison dashboard
- ⏭️ Trend analysis over time
- ⏭️ Slack/email notifications
- ⏭️ JIRA ticket creation for findings

## Why This Matters for Interviews

**Interviewers care about:**
1. Can you build **real** tools? ✅
2. Do you know security tools? ✅ (Trivy, Gitleaks)
3. Can you present complex data? ✅ (Dashboard)
4. Have you done this before? ✅ (Working code proves it)

**This project demonstrates:**
- DevSecOps pipeline automation
- Security tool integration
- Data persistence (SQLite)
- API design (FastAPI)
- Frontend visualization
- Real-world problem solving

## License

MIT

## Author

Built as a **functional security tool** - not just a demo.
Every feature works on real code.

---

## Next Steps

1. **Try it now:**
   ```bash
   python orbit-sec.py .
   ```

2. **Scan a real project:**
   ```bash
   python orbit-sec.py ~/your-project
   ```

3. **Add to your portfolio:**
   - Screenshot the dashboard with real findings
   - Record a demo video
   - Add to resume as "Built automated security scanner"

**No more fake data. This is the real deal.** 🛡️
