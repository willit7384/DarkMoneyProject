#!/bin/bash

while true; do
    echo "===== Starting scraper at $(date) ====="
    python3 ProPublicaNonProfit_api.py
    exit_code=$?

    echo "===== Scraper exited with code $exit_code ====="
    echo "Restarting in 30 seconds..."
    sleep 30
done
