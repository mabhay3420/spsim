#!/bin/bash
refresh=${1:""}

source .venv/bin/activate
# Run the complete pipeline (uses cache if present)
python scripts/run.py ${refresh}
