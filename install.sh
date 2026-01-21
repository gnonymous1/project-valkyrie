#!/bin/bash
# install.sh - Dependency Installer for Project Valkyrie

echo "[*] Checking for root privileges..."
if [ "$EUID" -ne 0 ]; then 
  echo "Please run as root (sudo ./install.sh)"
  exit
fi

echo "[*] Updating package lists..."
apt-get update

echo "[*] Installing system dependencies..."
# Added python3-venv to ensure we can create a virtual environment
apt-get install -y aircrack-ng reaver hcxtools wash python3-pip python3-venv

echo "[*] Setting up Python Virtual Environment (to avoid system conflicts)..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

echo "[*] Installing Python dependencies into venv..."
./venv/bin/pip install -r requirements.txt

echo "[+] Installation complete!"
echo "Run: sudo ./run.sh"
