"""
Shared fixtures & helpers for the test-suite.
"""
from __future__ import annotations
import pytest


@pytest.fixture()
def sample_uniprot_payload() -> dict:
    """
    Minimal UniProt-like JSON page with one human and one mouse record.

    It is small enough to fit entirely in-test yet realistic enough that the
    production parser (`species_similarity.fetch`) can consume it unchanged.
    """
    return {
        "results": [
            {
                "organism": {
                    "commonName": "Human",
                    "scientificName": "Homo sapiens",
                    "taxonId": 9606,
                },
                "sequence": {"value": "ACGT", "length": 4},
            },
            {
                "organism": {
                    "commonName": "Mouse",
                    "scientificName": "Mus musculus",
                    "taxonId": 10090,
                },
                "sequence": {"value": "ACGA", "length": 4},
            },
        ]
    }
