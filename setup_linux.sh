#!/bin/bash

# Script to set up Python virtual environment and install dependencies for the MPE Exporter tool on Linux.

VENV_DIR="venv"
REQUIREMENTS_FILE="requirements.txt"

echo "--- MPE Exporter Linux Setup ---"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. Check for Python 3
if ! command_exists python3; then
    echo "Error: Python 3 is not installed or not in PATH."
    echo "Please install Python 3 (e.g., 'sudo apt update && sudo apt install python3')."
    exit 1
fi
echo "Python 3 found."

# 2. Check for pip3
if ! command_exists pip3; then
    echo "Error: pip3 is not installed or not in PATH."
    echo "Please install pip3 for Python 3 (e.g., 'sudo apt install python3-pip')."
    exit 1
fi
echo "pip3 found."

# 3. Check for Python 3 venv module
if ! python3 -m venv -h >/dev/null 2>&1; then
    echo "Error: Python 3 'venv' module is not available."
    echo "Please install it (e.g., 'sudo apt install python3-venv')."
    exit 1
fi
echo "Python 3 venv module found."

# 4. Check for tkinter
echo "Checking for tkinter availability..."
if ! python3 -c "import tkinter" >/dev/null 2>&1; then
    echo "Warning: Python's tkinter module seems to be missing or not correctly installed."
    echo "This is often needed for matplotlib GUIs and other parts of the tool."
    echo "Please install the Tkinter development libraries for Python 3."
    echo "For Debian/Ubuntu: sudo apt-get install python3-tk"
    echo "For Fedora: sudo dnf install python3-tkinter"
    echo "After installation, you might need to re-run this script."
fi

# 5. Create virtual environment
if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment '$VENV_DIR' already exists. Skipping creation."
else
    echo "Creating virtual environment in './$VENV_DIR'..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment."
        exit 1
    fi
    echo "Virtual environment created."
fi

# 6. Activate virtual environment and install requirements
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "Installing dependencies from $REQUIREMENTS_FILE..."
pip3 install -r "$REQUIREMENTS_FILE"
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies."
    deactivate
    exit 1
fi

echo ""
echo "--- Setup Complete ---"
echo "To activate the virtual environment in your current terminal session, run:"
echo "  source $VENV_DIR/bin/activate"
echo "After activation, you can run the project's Python scripts."
echo "To deactivate, simply type 'deactivate'."