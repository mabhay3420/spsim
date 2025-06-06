"""
Display-oriented helpers built on top of `species_similarity.similarity`.

Separating these keeps `similarity.py` purely algorithmic while this module
may deal with HTML/CSS or other presentation concerns.
"""

from __future__ import annotations

from typing import Final

from .similarity import difference_mask

__all__ = ["html_colorise"]

_MISMATCH_STYLE: Final[str] = "color:red"


def html_colorise(
    sequence: str,
    reference: str,
    mismatch_style: str = _MISMATCH_STYLE,
) -> str:
    """
    Return an HTML string where nucleotides/amino-acids that differ from the
    *reference* are wrapped in a <span> with the given inline *mismatch_style*.

    Examples
    --------
    >>> html_colorise("ACGT", "ACGA")
    'A C G <span style="color:red">T</span>'
    """
    mask = difference_mask(reference, sequence)
    out_parts: list[str] = []
    for char, bit in zip(sequence, mask):
        if bit == "1":
            out_parts.append(f'<span style="{mismatch_style}">{char}</span>')
        else:
            out_parts.append(char)
    return "".join(out_parts)
