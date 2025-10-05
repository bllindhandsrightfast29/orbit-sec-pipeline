#!/bin/bash
# ORBIT-SEC Local Security Scanner
# Run this script before pushing code to catch vulnerabilities early

set -e  # Exit immediately on error
set -u  # Treat unset variables as errors

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  ORBIT-SEC Local Security Scan        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Change to project root
cd "$PROJECT_ROOT"

# Check if Trivy is installed
if ! command -v trivy &> /dev/null; then
    echo -e "${RED}ERROR: Trivy is not installed${NC}"
    echo ""
    echo "Install Trivy using one of these methods:"
    echo "  macOS:   brew install trivy"
    echo "  Linux:   wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -"
    echo "           echo \"deb https://aquasecurity.github.io/trivy-repo/deb \$(lsb_release -sc) main\" | sudo tee /etc/apt/sources.list.d/trivy.list"
    echo "           sudo apt-get update && sudo apt-get install trivy"
    echo "  Docker:  alias trivy='docker run --rm -v \$(pwd):/scan aquasec/trivy'"
    echo ""
    exit 1
fi

# Check if Gitleaks is installed
if ! command -v gitleaks &> /dev/null; then
    echo -e "${RED}ERROR: Gitleaks is not installed${NC}"
    echo ""
    echo "Install Gitleaks using one of these methods:"
    echo "  macOS:   brew install gitleaks"
    echo "  Linux:   wget https://github.com/gitleaks/gitleaks/releases/download/v8.18.0/gitleaks_8.18.0_linux_x64.tar.gz"
    echo "           tar -xzf gitleaks_8.18.0_linux_x64.tar.gz"
    echo "           sudo mv gitleaks /usr/local/bin/"
    echo "  Go:      go install github.com/gitleaks/gitleaks/v8@latest"
    echo ""
    exit 1
fi

# Initialize scan status
SCAN_FAILED=0

echo -e "${YELLOW}📦 Scanning dependencies with Trivy...${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if trivy fs . \
    --severity CRITICAL,HIGH \
    --exit-code 1 \
    --format table \
    --scanners vuln; then
    echo -e "${GREEN}✓ No critical vulnerabilities found in dependencies${NC}"
else
    echo -e "${RED}✗ CRITICAL or HIGH vulnerabilities detected!${NC}"
    SCAN_FAILED=1
fi

echo ""
echo -e "${YELLOW}🔍 Scanning for secrets with Gitleaks...${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if gitleaks detect \
    --source . \
    --verbose \
    --no-git 2>&1 | grep -v "^[0-9]"; then
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo -e "${GREEN}✓ No secrets detected${NC}"
    else
        echo -e "${RED}✗ Secrets detected in codebase!${NC}"
        SCAN_FAILED=1
    fi
else
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo -e "${GREEN}✓ No secrets detected${NC}"
    else
        echo -e "${RED}✗ Secrets detected in codebase!${NC}"
        SCAN_FAILED=1
    fi
fi

echo ""
echo -e "${YELLOW}🐳 Checking Dockerfile (if exists)...${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "Dockerfile" ]; then
    if trivy config Dockerfile \
        --severity CRITICAL,HIGH \
        --exit-code 0 \
        --format table; then
        echo -e "${GREEN}✓ Dockerfile check completed${NC}"
    else
        echo -e "${YELLOW}⚠ Dockerfile has configuration issues (non-blocking)${NC}"
    fi
else
    echo -e "${BLUE}ℹ No Dockerfile found, skipping...${NC}"
fi

echo ""
echo -e "${YELLOW}☁️ Scanning IaC configurations...${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -d "terraform" ]; then
    echo "Scanning Terraform files..."
    if trivy config terraform/ \
        --severity CRITICAL,HIGH,MEDIUM \
        --exit-code 0 \
        --format table; then
        echo -e "${GREEN}✓ Terraform scan completed${NC}"
    else
        echo -e "${YELLOW}⚠ Terraform has misconfigurations (non-blocking for local)${NC}"
        SCAN_FAILED=1
    fi
else
    echo -e "${BLUE}ℹ No terraform/ directory found${NC}"
fi

if [ -d "kubernetes" ]; then
    echo "Scanning Kubernetes manifests..."
    if trivy config kubernetes/ \
        --severity CRITICAL,HIGH,MEDIUM \
        --exit-code 0 \
        --format table; then
        echo -e "${GREEN}✓ Kubernetes scan completed${NC}"
    else
        echo -e "${YELLOW}⚠ Kubernetes manifests have issues (non-blocking for local)${NC}"
        SCAN_FAILED=1
    fi
else
    echo -e "${BLUE}ℹ No kubernetes/ directory found${NC}"
fi

echo ""
echo "════════════════════════════════════════"

if [ $SCAN_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All security checks passed!${NC}"
    echo -e "${GREEN}Safe to commit and push.${NC}"
    exit 0
else
    echo -e "${RED}❌ Security scan failed!${NC}"
    echo -e "${RED}Fix the issues above before pushing.${NC}"
    echo ""
    echo "Need help?"
    echo "  - Check docs/architecture.md for troubleshooting"
    echo "  - Review the CVE details and upgrade vulnerable packages"
    echo "  - Remove any detected secrets from your code"
    exit 1
fi
