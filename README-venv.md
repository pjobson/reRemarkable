# Virtual Environment Setup

This project now uses a Python virtual environment.

## Activation

To activate the virtual environment:
```bash
source venv/bin/activate
```

## System Dependencies

For full functionality, install these system packages:
```bash
# Ubuntu/Debian
sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-gtksource-3.0 gir1.2-webkit2-4.0

# For spell checking (optional)
pip install gtkspellcheck
```

## Running the Application

After activating the venv and installing system dependencies:
```bash
python3 remarkable
```