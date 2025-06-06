from __future__ import annotations

from species_similarity import pipeline
from species_similarity.config import SequenceRecord, Species


def test_build_distance_graph() -> None:
    human = SequenceRecord(Species("Human", "Homo sapiens", 9606), "ACGT")
    mouse = SequenceRecord(Species("Mouse", "Mus musculus", 10090), "ACGA")
    distances = [(human, 0), (mouse, 1)]
    g = pipeline.build_distance_graph(distances)
    assert set(g.nodes) == {"Human", "Mouse"}
    assert g.edges["Human", "Mouse"]["weight"] == 1
