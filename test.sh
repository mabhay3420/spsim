#!/bin/bash

source .venv/bin/activate
uv pip install -e .
pytest -q
