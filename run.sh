#!/bin/bash
foldername=`dirname $(readlink -f $0)`

PYTHON="$foldername/venv/bin/python3"
PIP="$foldername/venv/bin/pip"

if [ ! -f "$foldername/venv" ]; then
    python3 -m venv venv
fi

# Check if requirements are installed
if [ -f "$foldername/requirements.txt" ]; then
   # Check if all required packages are installed
   missing_packages=0
   while read -r package; do
       if [ -n "$package" ] && ! $PIP freeze | grep -qi "^${package%%[>=<]*}"; then
           missing_packages=1
           break
       fi
   done < "$foldername/requirements.txt"

   if [ $missing_packages -eq 1 ]; then
       echo "Installing missing requirements..."
       $PIP install -r "$foldername/requirements.txt"
   fi
fi

export PYTHONPATH=$foldername/reremarkable:$foldername/reremarkable_lib:$foldername
exec $PYTHON $foldername/bin/reremarkable "$@"
