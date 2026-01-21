#!/bin/bash
# run.sh - Launcher for Project Valkyrie

# Check for root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (sudo ./run.sh)"
  exit 1
fi


# Check if venv exists
if [ ! -d "venv" ]; then
    echo "[!] Virtual environment not found. Please run sudo ./install.sh first."
    exit 1
fi

echo "[*] Launching Agent (via venv)..."

# Activate virtual environment and run the application
source ./venv/bin/activate
./venv/bin/python main.py "$@"
deactivate
