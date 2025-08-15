# Virtual Environment Setup

This project now uses a Python virtual environment.

## Setup venv

```bash
python3 -m venv venv
```

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

```

## Running the Application

Run the application using:
```bash
./run.sh
```

The script will automatically use the virtual environment if available.
