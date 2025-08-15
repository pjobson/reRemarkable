#!/bin/bash
foldername=`dirname $(readlink -f $0)`

# Use virtual environment python if it exists
if [ -f "$foldername/venv/bin/python3" ]; then
    PYTHON="$foldername/venv/bin/python3"
else
    PYTHON="python3"
fi

PYTHONPATH=$foldername/remarkable:$foldername/remarkable_lib:$foldername exec $PYTHON $foldername/bin/remarkable "$@"
