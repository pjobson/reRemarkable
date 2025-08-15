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
sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-gtksource-3.0 gir1.2-webkit2-4.1

# For spell checking (optional), install system GTK development packages first:
sudo apt-get install libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-3.0
pip install pygtkspellcheck
```

## Running the Application

Run the application using:
```bash
./run.sh
```

The script will automatically use the virtual environment if available.