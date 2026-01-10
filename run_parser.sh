#!/bin/bash

while true; do
    echo "===== Starting parser at $(date) ====="
    python3 IRS990XML_Parser.py
    exit_code=$?

    echo "===== Parser exited with code $exit_code ====="
    echo "Restarting in 30 seconds..."
    sleep 30
done
