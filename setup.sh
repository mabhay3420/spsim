#!/bin/bash

pip install --upgrade uv 

# Create an in-project virtual environment and install all dependencies
uv sync --python-preference=only-managed 
source .venv/bin/activate
uv pip install -e .

# Run project
# ./run.sh

# Run the tests
# ./test.sh