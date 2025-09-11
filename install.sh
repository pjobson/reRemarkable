#!/bin/bash

# reRemarkable Installation Script
# This script installs reRemarkable markdown editor for Linux

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Get the directory where the script is located
reRemarkable=$(dirname $(readlink -f $0))
PIP="$reRemarkable/venv/bin/pip"

print_status "Starting reRemarkable installation..."
print_status "Installation directory: $reRemarkable"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed. Please install Python 3 first."
    exit 1
fi

# Check if pip is available
if ! python3 -m pip --version &> /dev/null; then
    print_error "pip is required but not available. Please install python3-pip first."
    exit 1
fi

# Check if venv module is available
if ! python3 -c "import venv" &> /dev/null; then
    print_error "Python venv module is required but not available. Please install python3-venv first."
    exit 1
fi

# Create config directory
print_status "Creating configuration directory..."
mkdir -p ~/.config/reremarkable
touch ~/.config/reremarkable/custom.css

# Install to /opt directory (requires sudo)
print_status "Installing to /opt directory (requires sudo permissions)..."
sudo mkdir -p /opt
if [ -d "/opt/reRemarkable" ]; then
    print_warning "Removing existing installation in /opt/reRemarkable..."
    sudo rm -rf /opt/reRemarkable
fi

sudo mkdir -p /opt/reRemarkable
sudo cp -r "$reRemarkable"/* /opt/reRemarkable/

# Create virtual environment
print_status "Creating Python virtual environment..."
if [ -d "/opt/reRemarkable/venv" ]; then
    print_warning "Virtual environment already exists, removing old one..."
    sudo rm -rf /opt/reRemarkable/venv
fi

sudo python3 -m venv /opt/reRemarkable/venv

PIP=/opt/reRemarkable/venv/bin/pip

# Install Python dependencies
print_status "Installing Python dependencies..."
sudo $PIP install --upgrade pip
sudo $PIP install -r requirements.txt

# Install desktop file
print_status "Installing desktop application entry..."
mkdir -p ~/.local/share/applications
cp /opt/reRemarkable/reremarkable.desktop ~/.local/share/applications/

# Install GSchema if gsettings is available
if command -v gsettings &> /dev/null; then
    print_status "Installing GSchema..."
    sudo mkdir -p /usr/share/glib-2.0/schemas/
    sudo cp /opt/reRemarkable/data/glib-2.0/schemas/net.launchpad.reremarkable.gschema.xml /usr/share/glib-2.0/schemas/
    sudo glib-compile-schemas /usr/share/glib-2.0/schemas/
else
    print_warning "gsettings not available, skipping GSchema installation"
fi

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    print_status "Updating desktop database..."
    update-desktop-database ~/.local/share/applications/
fi

print_success "reRemarkable has been successfully installed!"
print_status "You can now:"
print_status "- Launch reRemarkable from your application menu"
print_status "- Run '/opt/reRemarkable/run.sh' from the command line"
print_status "- Uninstall using '/opt/reRemarkable/uninstall.sh'"

