#!/bin/bash

cd $1

source venv/bin/activate
msg=$(python search_updates.py)
deactivate

if [ -z "$msg" ]; then
    echo "No updates found."
    exit 0
fi

echo "$msg"

cd ../remote_logs
source venv/bin/activate
python send_logs.py "versions" "$msg"
deactivate