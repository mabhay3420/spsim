# species-similarity
Beta-globin sequence comparison across species
=============================================

This project fetches every available HBB (beta-globin) sequence from UniProt,
computes Hamming distances to the human sequence, and renders an HTML page in
which *Homo sapiens* is at the center and all other species are placed on
concentric rings according to their distance.

--------------------------------------------------------------------
1. Quick start
--------------------------------------------------------------------

```bash
# Install uv (fast package manager) if you do not have it
pip install --upgrade uv

# Clone and enter the repository
git clone https://github.com/your-org/species-similarity.git
cd species-similarity

# Create an in-project virtual environment and install all dependencies
uv venv 
uv pip install -e .

# Run the complete pipeline
python scripts/run.py            # uses cache if present
python scripts/run.py --refresh  # force fresh download
