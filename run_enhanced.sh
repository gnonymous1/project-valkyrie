#!/bin/bash
# Enhanced Project Valkyrie launcher script

echo "🚀 Launching PROJECT VALKYRIE: Enhanced Edition"

# Check if running with sudo (required for wireless operations)
if [[ $EUID -eq 0 ]]; then
   echo "⚠️  WARNING: Running as root. This is dangerous and not recommended."
   echo "Consider configuring proper udev rules instead of running as root."
   echo "Continuing in 3 seconds..."
   sleep 3
fi

# Check if virtual environment exists, if not create it
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements if not already installed
echo "📥 Installing/updating requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# Export GEMINI_API_KEY if it exists in environment
if [ -z "$GEMINI_API_KEY" ]; then
    if [ -f ".env" ]; then
        export $(grep -v '^#' .env | xargs)
    fi
fi

# Run the enhanced application
echo "🎮 Starting Enhanced UI..."
python main.py "$@"