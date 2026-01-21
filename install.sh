#!/bin/bash
# install.sh - Dependency Installer for Project Valkyrie (Autonomous Interdiction Swarm)

echo "[*] checking for root privileges..."
if [ "$EUID" -ne 0 ]; then 
  echo "Please run as root (sudo ./install.sh)"
  exit
fi

echo "[*] Updating package lists..."
apt-get update

echo "[*] Installing system dependencies (aircrack-ng, reaver, hcxtools)..."
# -y to auto approve
apt-get install -y aircrack-ng reaver hcxtools wash python3-pip

echo "[*] Installing Python dependencies..."
pip install -r requirements.txt --break-system-packages

echo "[+] Installation complete!"
echo "Run: sudo ./run.sh"
