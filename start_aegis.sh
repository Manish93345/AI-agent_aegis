#!/bin/bash

echo "========================================"
echo "     Starting AEGIS System"
echo "========================================"

# Check Python version
python3 --version | grep -q "Python 3\.[9-9]" || {
    echo "Python 3.9+ required"
    exit 1
}

# Activate virtual environment
if [ -d "aegis_venv" ]; then
    source aegis_venv/bin/activate
else
    echo "Virtual environment not found. Creating..."
    python3 -m venv aegis_venv
    source aegis_venv/bin/activate
    pip install --upgrade pip
fi

# Install requirements
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found!"
    exit 1
fi

# Run AEGIS
echo ""
echo "Starting AEGIS..."
python3 main.py

echo ""
echo "AEGIS has stopped."