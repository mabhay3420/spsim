#!/bin/bash

pip install --upgrade uv

# Clone and enter the repository
git clone https://github.com/mabhay3420/species-similarity.git
cd species-similarity

# Create an in-project virtual environment and install all dependencies
uv venv -p 3.9
source .venv/bin/activate
uv pip install -e .

# Run the complete pipeline
python scripts/run.py            # uses cache if present