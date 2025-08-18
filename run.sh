#!/bin/bash
foldername=$(dirname $(readlink -f "$0"))

PYTHON="$foldername/venv/bin/python3"
PIP="$foldername/venv/bin/pip"

# Create virtual environment if it doesn't exist
if [ ! -d "$foldername/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$foldername/venv"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment"
        exit 1
    fi
fi

# Check if Python exists in venv
if [ ! -f "$PYTHON" ]; then
    echo "Error: Virtual environment Python not found at $PYTHON"
    exit 1
fi

# Check if requirements are installed
if [ -f "$foldername/requirements.txt" ]; then
    # Check if all required packages are installed
    missing_packages=0
    
    while IFS= read -r package || [ -n "$package" ]; do
        # Skip empty lines and comments
        if [ -z "$package" ] || echo "$package" | grep -q "^#"; then
            continue
        fi
        
        # Extract package name (remove version specifiers like >=, ==, etc.)
        package_name=$(echo "$package" | sed 's/[><=!].*//' | tr -d ' ')
        
        if [ -n "$package_name" ]; then
            if ! "$PIP" freeze | grep -qi "^$package_name=="; then
                missing_packages=1
                break
            fi
        fi
    done < "$foldername/requirements.txt"

    if [ $missing_packages -eq 1 ]; then
        echo "Installing missing requirements..."
        "$PIP" install -r "$foldername/requirements.txt"
        if [ $? -ne 0 ]; then
            echo "Error: Failed to install requirements"
            exit 1
        fi
    fi
fi

# Set Python path and run the application
export PYTHONPATH="$foldername/reremarkable:$foldername/reremarkable_lib:$foldername"
exec "$PYTHON" "$foldername/bin/reremarkable" "$@"
