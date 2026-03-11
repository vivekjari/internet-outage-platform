#!/bin/bash
# Quick setup script for Internet Outage Platform

set -e

echo "======================================"
echo "Internet Outage Platform - Setup"
echo "======================================"
echo ""

# Check Python version
echo "✓ Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Python version: $python_version"

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo "✓ Creating virtual environment..."
    python3 -m venv .venv
else
    echo "✓ Virtual environment already exists"
fi

# Activate venv
echo "✓ Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "✓ Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Configure your database in config.py (or set environment variables)"
echo "2. Set CLOUDFLARE_API_TOKEN environment variable"
echo "3. Run ingestion scripts:"
echo "   - python ingest_cloudflare.py"
echo "   - python ingest_ai_bots.py"
echo "   - python ingest_device_type.py"
echo ""
echo "To deploy to GitHub:"
echo "1. Read DEPLOYMENT.md for detailed instructions"
echo "2. Create a repository on GitHub"
echo "3. Follow the 'Connect Local Repository' section"
echo ""
