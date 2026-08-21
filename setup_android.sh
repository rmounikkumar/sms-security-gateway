#!/bin/bash
# =============================================
# SMS Security Gateway - Android One-Click Setup
# Run this script in Termux to set up everything
# =============================================

set -e

echo ""
echo "========================================"
echo "  SMS Security Gateway - Android Setup"
echo "========================================"
echo ""

# Step 1: Update Termux
echo "[1/6] Updating Termux..."
pkg update -y && pkg upgrade -y

# Step 2: Install Python and dependencies
echo "[2/6] Installing Python..."
pkg install python git -y

# Step 3: Install Python packages
echo "[3/6] Installing Python packages (may take 10-15 min)..."
pip install flask transformers torch --no-cache-dir

# Step 4: Clone the project
echo "[4/6] Cloning project..."
if [ -d "sms-security-gateway" ]; then
    cd sms-security-gateway
    git pull
else
    git clone https://github.com/rmounikkumar/sms-security-gateway.git
    cd sms-security-gateway
fi

# Step 5: Create required directories
echo "[5/6] Setting up directories..."
mkdir -p data quarantine logs

# Step 6: Download BERT model
echo "[6/6] Downloading BERT-Tiny model..."
python -c "from transformers import pipeline; pipeline('text-classification', model='mrm8488/bert-tiny-finetuned-sms-spam-detection'); print('Model downloaded OK')"

echo ""
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo ""
echo "To start the server:"
echo "  cd sms-security-gateway"
echo "  python app.py"
echo ""
echo "Then open in phone browser:"
echo "  http://localhost:5000"
echo ""
echo "========================================"
