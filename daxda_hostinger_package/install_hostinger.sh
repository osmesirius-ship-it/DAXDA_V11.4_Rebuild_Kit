#!/bin/bash
# DAXDA V11.4 Hostinger Automated SSH Setup Script

echo "======================================================"
echo "      DAXDA V11.4 Hostinger Deployment Installer"
echo "======================================================"

# 1. Environment check
PYTHON_BIN=$(which python3 || which python)
if [ -z "$PYTHON_BIN" ]; then
    echo "[ERROR] Python 3 not found in PATH."
    exit 1
fi

echo "[1/4] Found Python binary: $PYTHON_BIN"

# 2. Virtualenv setup if requested
if [ ! -d "venv" ]; then
    echo "[2/4] Creating virtual environment (venv)..."
    $PYTHON_BIN -m venv venv
fi

echo "[3/4] Activating virtual environment & installing requirements..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 3. Running Preflight Test
echo "[4/4] Verifying DAXDA engine installation..."
python run_preflight.py

echo ""
echo "======================================================"
echo " [SUCCESS] DAXDA V11.4 installed on Hostinger!"
echo " Web App Entry: passenger_wsgi.py (Flask Dashboard)"
echo " To run standalone: python app.py"
echo "======================================================"
