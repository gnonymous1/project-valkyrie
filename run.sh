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
    echo "    Or edit this script to set it."
    # Optional: read -p "Enter API Key (or press Enter to skip): " key
fi

# Run the agent
# Preserve env vars with -E if user exported key
echo "[*] Launching Agent..."
python3 main.py "$@"
