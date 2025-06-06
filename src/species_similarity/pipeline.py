from __future__ import annotations

from pathlib import Path
from typing import Final, Optional
import logging

import pandas as pd

from .config import DATA_PROCESSED, SequenceRecord, Species
from .fetch import fetch_gene_sequences, DEFAULT_GENE
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


def _save_records(recs: list[SequenceRecord], path: Path) -> None:
    """Write flat CSV so pandas does not stringify the dataclass."""
    logger = logging.getLogger(__name__)
    rows = [
        {
            "common_name": r.species.common_name,
            "scientific_name": r.species.scientific_name,
            "taxonomy_id": r.species.taxonomy_id,
            "sequence": r.sequence,
        }
        for r in recs
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Saving records to %s", path)
    pd.DataFrame(rows).to_csv(path, index=False)


def _load_records(path: Path) -> list[SequenceRecord]:
    """Recreate SequenceRecord objects from the flat CSV."""
    logger = logging.getLogger(__name__)
    logger.info("Loading records from %s", path)
    df = pd.read_csv(path)
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


def run(
    force_refresh: bool = False,
    gene: str = DEFAULT_GENE,
    csv_all: Optional[Path] = None,
    csv_close: Optional[Path] = None,
    html_out: Optional[Path] = None,
) -> Path:
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
    logger = logging.getLogger(__name__)
    logger.info("Starting pipeline")

    csv_all = csv_all or (
        CSV_ALL
        if gene == DEFAULT_GENE
        else DATA_PROCESSED / f"{gene}_all_sequences.csv"
    )
    csv_close = csv_close or (
        CSV_CLOSE
        if gene == DEFAULT_GENE
        else DATA_PROCESSED / f"{gene}_close_to_human.csv"
    )
    html_out = html_out or (
        HTML_OUT
        if gene == DEFAULT_GENE
        else DATA_PROCESSED / f"{gene}_close_to_human.html"
    )
    # 1) Fetch or use cached data
    if force_refresh or not csv_all.exists():
        logger.info("Fetching sequences from UniProt")
        records = fetch_gene_sequences(gene)
        _save_records(records, csv_all)

    records = _load_records(csv_all)

    # 2) Similarity scores
    logger.info("Computing similarity distances")
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

    logger.info("Writing close species CSV to %s", csv_close)
    df.to_csv(csv_close, index=False)

    # 3) Render concentric-circle HTML
    logger.info("Rendering HTML report to %s", html_out)
    return render_html(df.sort_values("hamming_distance"), html_out)
