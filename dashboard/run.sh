#!/bin/bash
# Quick start script for ORBIT-SEC Dashboard

set -e

cd "$(dirname "$0")"

echo "🛡️  ORBIT-SEC Security Dashboard"
echo "================================"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "🚀 Starting dashboard server..."
echo "📊 Dashboard: http://localhost:8000"
echo "📡 API Docs:  http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run dashboard
python dashboard.py
