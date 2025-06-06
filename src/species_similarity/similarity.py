"""
Core similarity logic: Hamming distance + diff mask utilities.
"""

from __future__ import annotations
from rapidfuzz.distance import Levenshtein


from typing import Iterable

from .config import SequenceRecord

__all__ = [
    "hamming",
    "edit_distance",
    "difference_mask",
    "compute_distances",
]


def hamming(a: str, b: str) -> int:
    """
    Compute the Hamming distance between two *equal-length* strings.

    Raises
    ------
    ValueError
        If the sequences have unequal length.
    """
    if len(a) != len(b):
        raise ValueError("Sequences must be equal length")
    return sum(c1 != c2 for c1, c2 in zip(a, b))


def edit_distance(a: str, b: str) -> int:
    return Levenshtein.distance(a, b)   # substitutions + indels



def difference_mask(ref: str, other: str) -> str:
    """
    Return a minimal-length mask that flags only the characters *present in
    `other`* which differ from `ref` when the two strings are optimally
    aligned (Levenshtein optimum).

    The mask length is therefore **len(other)**, not the longer of the two
    strings, and it contains:

        '0' – the character in `other` aligns to the same
        '1' – the character in `other` is substituted for, or is an insertion

    Deletions in `other` do not create a mask position because they do not
    correspond to any character in `other`.

    Examples
    --------
    >>> difference_mask("ACGT", "ACGA")
    '0001'
    >>> difference_mask("ACGT", "ACGTA")      # insertion at end
    '00001'
    >>> difference_mask("ACGT", "AGT")        # deletion of 'C'
    '001'        # only 'G','T' considered; 'A' and 'G' match, 'T' differs
    """
    # Initialise all positions in `other` as matches
    mask = ["0"] * len(other)

    # Levenshtein.editops gives a minimal edit script
    # Types: "replace", "delete", "insert"
    for op in Levenshtein.editops(ref, other):
        if op.tag in ("replace", "insert"):
            # For replace/insert the destination index refers to `other`
            mask[op.dest_pos] = "1"
        # "delete" touches only `ref`; nothing to mark in `other`

    return "".join(mask)



def compute_distances(
    records: Iterable[SequenceRecord],
) -> list[tuple[SequenceRecord, int]]:
    """
    Given an iterable of `SequenceRecord`s that *must* include a
    Human (common_name == 'Human'), return a list of pairs
    *(record, hamming_distance_to_human)*.
    """
    recs = list(records)
    try:
        human_seq = next(
            r.sequence for r in recs if r.species.common_name.lower() == "human"
        )
    except StopIteration as exc:  # pragma: no cover
        raise ValueError("Human sequence not present in record set") from exc

    return [(rec, edit_distance(rec.sequence, human_seq)) for rec in recs]