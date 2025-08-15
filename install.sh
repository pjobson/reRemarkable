#!/bin/bash

reRemarkable=`dirname $(readlink -f $0)`

PIP="$reRemarkable/venv/bin/pip"

mkdir -p ~/.config/reremarkable
python3 -m venv venv
$PIP install -r requirements.txt
sudo mkdir -p /opt
sudo cp -r $reRemarkable /opt/
cp reremarkable.desktop ~/.local/share/applications

