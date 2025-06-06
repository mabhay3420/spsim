from __future__ import annotations

from pathlib import Path
from typing import Final

import pandas as pd

from .config import DATA_PROCESSED, SequenceRecord, Species
from .fetch import fetch_all_beta_globin_sequences
from .similarity import compute_distances, difference_mask
from .images import image_url
from .render import render_concentric as render_html

# --------------------------------------------------------------------- #
#  Paths                                                                #
# --------------------------------------------------------------------- #

CSV_ALL: Final[Path] = DATA_PROCESSED / "all_beta_globin_sequences.csv"
CSV_CLOSE: Final[Path] = DATA_PROCESSED / "close_to_human.csv"
HTML_OUT: Final[Path] = DATA_PROCESSED / "close_to_human.html"

# --------------------------------------------------------------------- #
#  Helpers for (de)serialising SequenceRecord                           #
# --------------------------------------------------------------------- #


def _save_records(recs: list[SequenceRecord]) -> None:
    """Write flat CSV so pandas does not stringify the dataclass."""
    rows = [
        {
            "common_name": r.species.common_name,
            "scientific_name": r.species.scientific_name,
            "taxonomy_id": r.species.taxonomy_id,
            "sequence": r.sequence,
        }
        for r in recs
    ]
    CSV_ALL.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(CSV_ALL, index=False)


def _load_records() -> list[SequenceRecord]:
    """Recreate SequenceRecord objects from the flat CSV."""
    df = pd.read_csv(CSV_ALL)
    return [
        SequenceRecord(
            Species(row.common_name, row.scientific_name, int(row.taxonomy_id)),
            row.sequence,
        )
        for row in df.itertuples(index=False)
    ]


# --------------------------------------------------------------------- #
#  Public pipeline entry point                                          #
# --------------------------------------------------------------------- #


def run(force_refresh: bool = False) -> Path:
    """
    End-to-end pipeline.

    Parameters
    ----------
    force_refresh
        Ignore cached CSV and fetch from UniProt again.

    Returns
    -------
    Path
        Location of the generated HTML report.
    """
    # 1) Fetch or use cached data
    if force_refresh or not CSV_ALL.exists():
        records = fetch_all_beta_globin_sequences()
        _save_records(records)

    records = _load_records()

    # 2) Similarity scores
    distances = compute_distances(records)
    human_seq = next(
        r.sequence for r in records if r.species.common_name.lower() == "human"
    )

    df = pd.DataFrame(
        {
            "name": r.species.common_name,
            "scientific_name": r.species.scientific_name,
            "taxonomy_id": r.species.taxonomy_id,
            "sequence": r.sequence,
            "sequence_length": len(r.sequence),
            "hamming_distance": dist,
            "image_url": image_url(r.species.scientific_name) or "N/A",
            "different": difference_mask(human_seq, r.sequence),
        }
        for r, dist in distances
    )

    df.to_csv(CSV_CLOSE, index=False)

    # 3) Render concentric-circle HTML
    return render_html(df.sort_values("hamming_distance"), HTML_OUT)
