#!/bin/bash
# run.sh - Launcher for Project Valkyrie

# Check for root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (sudo ./run.sh)"
  exit
fi

# Check for Gemini API Key
if [ -z "$GEMINI_API_KEY" ]; then
    echo "[!] GEMINI_API_KEY environment variable not found."
    echo "    AI features will be disabled."
    echo "    To enable, run: export GEMINI_API_KEY='your_key' before sudo -E ./run.sh"
    # Optional: read -p "Enter API Key (or press Enter to skip): " key
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "[!] Virtual environment not found. Please run sudo ./install.sh first."
    exit 1
fi

echo "[*] Launching Agent (via venv)..."
# Run python from the venv directly
./venv/bin/python main.py "$@"
