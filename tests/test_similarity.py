from __future__ import annotations
import pytest
from species_similarity.similarity import (
    hamming,
    difference_mask,
    compute_distances,
)
from species_similarity.config import SequenceRecord, Species


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [("AAA", "AAA", 0), ("AAA", "AAT", 1), ("GATTACA", "GACTATA", 2)],
)
def test_hamming(a: str, b: str, expected: int) -> None:
    """Classic correctness table for the Hamming implementation."""
    assert hamming(a, b) == expected


def test_difference_mask() -> None:
    assert difference_mask("ACGT", "ACGA") == "0001"


def test_compute_distances_arbitrary_reference() -> None:
    records = [
        SequenceRecord(Species("Human", "Homo sapiens", 9606), "ACGT"),
        SequenceRecord(Species("Mouse", "Mus musculus", 10090), "ACGA"),
        SequenceRecord(Species("Rat", "Rattus norvegicus", 10116), "ACGG"),
    ]

    distances = compute_distances(records, reference_common_name="Mouse")
    # Order preserved
    assert [d for _, d in distances] == [1, 0, 1]


def test_compute_distances_missing_reference() -> None:
    records = [
        SequenceRecord(Species("Human", "Homo sapiens", 9606), "ACGT"),
    ]
    with pytest.raises(ValueError):
        compute_distances(records, reference_common_name="Cat")
