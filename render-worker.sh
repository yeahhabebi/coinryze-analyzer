#!/usr/bin/env bash
set -e

echo "=== Starting Coinryze Worker ==="

# Activate virtual environment if needed (Render automatically installs deps)
# cd into fetcher directory
cd "$(dirname "$0")"

# Run the fetcher in blocking mode (APScheduler runs inside)
python fetcher/fetch_coinryze.py
