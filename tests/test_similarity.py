from __future__ import annotations
import pytest
from species_similarity.similarity import hamming, difference_mask


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [("AAA", "AAA", 0), ("AAA", "AAT", 1), ("GATTACA", "GACTATA", 2)],
)
def test_hamming(a: str, b: str, expected: int) -> None:
    """Classic correctness table for the Hamming implementation."""
    assert hamming(a, b) == expected


def test_difference_mask() -> None:
    assert difference_mask("ACGT", "ACGA") == "0001"
