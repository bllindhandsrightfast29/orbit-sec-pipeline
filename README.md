# DevSecOps Security Pipeline Demo

A demonstration project showcasing automated security scanning in CI/CD pipelines.

## Overview

This project contains an intentionally vulnerable Flask application used to demonstrate:
- Dependency vulnerability scanning with Trivy
- Secret detection with Gitleaks
- Automated security gates in GitHub Actions
- Security-first CI/CD practices

## ⚠️ Security Notice

**This application contains intentional security vulnerabilities for educational purposes.**
- Do NOT deploy to production
- Do NOT expose to the internet
- For learning and portfolio demonstration only

## Vulnerabilities Included

### Dependency Vulnerabilities
- Flask 2.0.1 (CVE-2023-30861)
- requests 2.25.0 (outdated)
- urllib3 1.26.4 (CVE-2021-33503)

### Code Vulnerabilities
- Server-Side Template Injection (SSTI)
- Server-Side Request Forgery (SSRF)
- Hardcoded secrets
- Debug mode enabled
- Sensitive data exposure

## Project Structure

```
devsecops-pipeline/
├── app.py                    # Vulnerable Flask application
├── requirements.txt          # Dependencies with known CVEs
├── Dockerfile               # Container configuration
├── .github/
│   └── workflows/
│       └── security.yml     # Security scanning pipeline
└── README.md               # This file
```

## Roadmap

- [x] Week 1: Setup & Foundation
- [ ] Week 2: First Security Gate (Trivy scanning)
- [ ] Week 3: Secrets Detection (Gitleaks)
- [ ] Week 4: Polish & Documentation
- [ ] Week 5: Demo & Portfolio

## Running Locally

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py

# Visit http://localhost:5000
```

## Running with Docker

```bash
# Build image
docker build -t devsecops-demo .

# Run container
docker run -p 5000:5000 devsecops-demo
```

## License

MIT License - Educational purposes only
