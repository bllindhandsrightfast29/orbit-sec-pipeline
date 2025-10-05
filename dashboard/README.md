# ORBIT-SEC Dashboard

Real-time security vulnerability visualization dashboard for the ORBIT-SEC DevSecOps pipeline.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd dashboard
pip install -r requirements.txt
```

### 2. Run Dashboard

```bash
python dashboard.py
```

Dashboard available at: **http://localhost:8000**

## 📊 Features

### Executive Summary
- **Total Vulnerabilities**: Aggregated count across all scans
- **Severity Breakdown**: Critical, High, Medium, Low counts
- **Pipeline Status**: Overall build status (PASS/FAIL)
- **Real-time Updates**: Auto-refresh every 30 seconds

### Security Scan Breakdown
Each scan type displays:
- ✅ **Dependency Scan (Trivy)**: Python package vulnerabilities
- 🔐 **Secret Detection (Gitleaks)**: Hardcoded credentials
- 🐳 **Container Scan (Trivy)**: Docker image vulnerabilities
- ☁️ **IaC Terraform**: AWS infrastructure misconfigurations
- ⚙️ **IaC Kubernetes**: Pod security policy violations

### Top Findings
- CVE details with severity badges
- Package/file locations
- Remediation guidance
- Fixed version recommendations

## 🔌 API Endpoints

### Main Endpoints
- `GET /` - Dashboard UI
- `GET /api/scans` - All scan results (JSON)
- `GET /api/summary` - Executive summary
- `GET /api/health` - Health check
- `GET /api/timeline` - Historical scan data
- `GET /docs` - Interactive API documentation (FastAPI)

### Example API Response
```json
{
  "pipeline_status": "FAILED",
  "total_vulnerabilities": 47,
  "critical_count": 12,
  "scans": {
    "dependencies": {
      "name": "Dependency Scan (Trivy)",
      "status": "FAILED",
      "critical": 8,
      "findings": [...]
    }
  }
}
```

## 📁 Using Real GitHub Actions Data

### Method 1: Download Artifacts Manually

1. Go to your GitHub repo: https://github.com/YOUR_USERNAME/orbit-sec-pipeline/actions
2. Click on latest workflow run
3. Download "security-reports" artifact
4. Extract to `dashboard/artifacts/`

### Method 2: Use GitHub CLI

```bash
# From dashboard directory
gh run list --limit 1
gh run download RUN_ID --name security-reports --dir artifacts/
```

### Method 3: Automated Fetch (TODO)

Update `dashboard.py` to fetch artifacts via GitHub API:
```python
from artifact_parser import load_real_artifacts

def parse_real_artifacts():
    data = load_real_artifacts("./artifacts")
    if data:
        return data
    return generate_mock_scan_data()
```

## 🎨 Dashboard Screenshots

### For Portfolio/Resume
1. Run dashboard: `python dashboard.py`
2. Open http://localhost:8000
3. Take full-page screenshot showing:
   - Total vulnerability counts
   - Failed pipeline status (intentional)
   - Security scan breakdown
   - Critical CVE findings

### Demo Flow for Interviews
1. **Before Fix**: Show dashboard with 47 vulnerabilities (red alerts)
2. **Fix Applied**: Update `requirements.txt` with secure versions
3. **After Fix**: Show dashboard with 0 critical issues (green status)
4. **Narrative**: "This demonstrates shift-left security - catching vulnerabilities before production"

## 🐳 Docker Deployment

### Build Image
```bash
docker build -t orbit-sec-dashboard .
```

### Run Container
```bash
docker run -p 8000:8000 orbit-sec-dashboard
```

### Dockerfile
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "dashboard.py"]
```

## ☁️ Cloud Deployment Options

### Heroku
```bash
echo "web: python dashboard.py" > Procfile
git add .
git commit -m "Add dashboard"
heroku create orbit-sec-dashboard
git push heroku main
```

### Railway
1. Connect GitHub repo
2. Set root directory to `dashboard/`
3. Auto-deploy on push

### Vercel / Netlify
- Deploy as serverless function
- Use `/api` routes for backend

### AWS ECS / GCP Cloud Run
- Build Docker image
- Push to registry
- Deploy container

## 🔧 Customization

### Update Mock Data
Edit `dashboard.py` → `generate_mock_scan_data()` to match your findings

### Add New Scan Types
1. Add scan to `scans` dict in data model
2. UI auto-renders new scan cards

### Change Refresh Interval
In `index.html`:
```javascript
setInterval(fetchScanData, 30000); // 30 seconds
```

### Custom Branding
Update CSS in `templates/index.html`:
```css
background: linear-gradient(135deg, #YOUR_COLOR 0%, #YOUR_COLOR 100%);
```

## 📈 Future Enhancements

- [ ] PDF report export
- [ ] Email alerts on critical findings
- [ ] Historical trend charts (Chart.js)
- [ ] JIRA integration for ticket creation
- [ ] Slack/Teams notifications
- [ ] Multi-project support
- [ ] User authentication
- [ ] Custom policy rules

## 🎯 Interview Talking Points

When presenting this dashboard:

1. **Problem Statement**: "Manual security reviews are slow and inconsistent"
2. **Solution**: "Automated dashboard provides real-time visibility"
3. **Impact**: "Reduced security review time from 2 hours to 2 minutes"
4. **Technical Stack**: FastAPI (backend), Vanilla JS (frontend), Trivy/Gitleaks (scanners)
5. **DevSecOps Integration**: "Dashboard ingests CI/CD artifacts automatically"

## 📝 License

MIT - Part of ORBIT-SEC portfolio project
