"""
Core similarity logic: Hamming distance + diff mask utilities.
"""

from __future__ import annotations
from rapidfuzz.distance import Levenshtein


from typing import Iterable
import logging
from tqdm.auto import tqdm

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
    return Levenshtein.distance(a, b)  # substitutions + indels


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
    reference_common_name: str = "Human",
) -> list[tuple[SequenceRecord, int]]:
    """Return distances from each record to the reference species.

    Parameters
    ----------
    records
        Iterable of ``SequenceRecord`` instances.
    reference_common_name
        The ``common_name`` of the species to which all distances should be
        computed.  Defaults to ``"Human"`` for backwards compatibility.

    Raises
    ------
    ValueError
        If the reference species is not present in ``records``.
    """
    logger = logging.getLogger(__name__)

    recs = list(records)
    try:
        ref_seq = next(
            r.sequence
            for r in recs
            if r.species.common_name.lower() == reference_common_name.lower()
        )
    except StopIteration as exc:  # pragma: no cover
        logger.error("Reference '%s' not present in record set", reference_common_name)
        raise ValueError(
            f"Reference species '{reference_common_name}' not present"
        ) from exc

    distances: list[tuple[SequenceRecord, int]] = []
    for rec in tqdm(recs, desc="Computing distances", unit="seq", leave=False):
        dist = edit_distance(rec.sequence, ref_seq)
        logger.debug(
            "Distance to %s for %s: %d",
            reference_common_name,
            rec.species.common_name,
            dist,
        )
        distances.append((rec, dist))

    return distances
