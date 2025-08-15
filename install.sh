#!/bin/bash

mkdir -p ~/.config/remarkable
python3 -m venv venv
sudo mkdir -p /opt
sudo cp ../Remarkable /opt/
cp remarkable.desktop ~/.local/share/applications

