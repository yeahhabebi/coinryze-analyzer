#!/usr/bin/env bash
# render-worker.sh

# Install dependencies (optional if Render already does it)
pip install -r requirements.txt

# Run the fetcher script
python3 fetcher/fetch_coinryze.py
