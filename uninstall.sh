#!/bin/bash

# reRemarkable Uninstallation Script
# This script removes reRemarkable markdown editor from your system

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

print_status "Starting reRemarkable uninstallation..."

# Confirm uninstallation
read -p "Are you sure you want to uninstall reRemarkable? This will remove all application data. (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_status "Uninstallation cancelled."
    exit 0
fi

# Remove desktop application entry
if [ -f ~/.local/share/applications/reremarkable.desktop ]; then
    print_status "Removing desktop application entry..."
    rm ~/.local/share/applications/reremarkable.desktop
    print_success "Desktop entry removed"
else
    print_warning "Desktop entry not found"
fi

# Remove GSchema if it exists
if [ -f /usr/share/glib-2.0/schemas/net.launchpad.reremarkable.gschema.xml ]; then
    print_status "Removing GSchema (requires sudo permissions)..."
    sudo rm -f /usr/share/glib-2.0/schemas/net.launchpad.reremarkable.gschema.xml
    if command -v glib-compile-schemas &> /dev/null; then
        sudo glib-compile-schemas /usr/share/glib-2.0/schemas/
    fi
    print_success "GSchema removed"
fi

# Remove installation directory
if [ -d /opt/reRemarkable ]; then
    print_status "Removing installation directory (requires sudo permissions)..."
    sudo rm -rf /opt/reRemarkable
    print_success "Installation directory removed"
else
    print_warning "Installation directory not found"
fi

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    print_status "Updating desktop database..."
    update-desktop-database ~/.local/share/applications/ 2>/dev/null || true
fi

print_success "reRemarkable has been successfully uninstalled!"
print_status "Thank you for using reRemarkable."
