#!/bin/bash
# install.sh - Dependency Installer for Project Valkyrie

echo "[*] Checking for root privileges..."
if [ "$EUID" -ne 0 ]; then 
  echo "Please run as root (sudo ./install.sh)"
  exit 1
fi

echo "[*] Updating package lists..."
apt-get update

echo "[*] Installing system dependencies..."
# Install all necessary wireless security tools
apt-get install -y aircrack-ng reaver bully hcxtools hcxdumptool tshark python3-pip python3-venv

echo "[*] Setting up Python Virtual Environment (to avoid system conflicts)..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

echo "[*] Installing Python dependencies into venv..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

echo "[+] Installation complete!"
echo "Run: sudo ./run.sh"
