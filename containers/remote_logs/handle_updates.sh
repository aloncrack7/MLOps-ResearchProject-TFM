#!/bin/bash

msg=$(/app/venv/bin/python3 search_updates.py)

if [ -z "$msg" ]; then
    echo "No updates found."
    exit 0
fi

echo "$msg"

/app/venv/bin/python3 send_logs.py "versions" "$msg"