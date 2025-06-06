from __future__ import annotations
import json

from pathlib import Path
from typing import Final, Iterable
import logging

import networkx as nx

import pandas as pd

from .config import DATA_PROCESSED, SequenceRecord, Species
from .fetch import fetch_all_beta_globin_sequences
from .similarity import compute_distances, difference_mask
from .images import image_url
from .render import render_concentric as render_html
from . import nx_vis

# --------------------------------------------------------------------- #
#  Paths                                                                #
# --------------------------------------------------------------------- #

CSV_ALL: Final[Path] = DATA_PROCESSED / "all_beta_globin_sequences.csv"
CSV_CLOSE: Final[Path] = DATA_PROCESSED / "close_to_human.csv"
HTML_OUT: Final[Path] = DATA_PROCESSED / "close_to_human.html"
GRAPH_HTML: Final[Path] = DATA_PROCESSED / "edit_distance_graph.html"
GRAPH_JSON: Final[Path] = DATA_PROCESSED / "force" / "force.json"

# --------------------------------------------------------------------- #
#  Helpers for (de)serialising SequenceRecord                           #
# --------------------------------------------------------------------- #


def _save_records(recs: list[SequenceRecord]) -> None:
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
    CSV_ALL.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Saving records to %s", CSV_ALL)
    pd.DataFrame(rows).to_csv(CSV_ALL, index=False)


def _load_records() -> list[SequenceRecord]:
    """Recreate SequenceRecord objects from the flat CSV."""
    logger = logging.getLogger(__name__)
    logger.info("Loading records from %s", CSV_ALL)
    df = pd.read_csv(CSV_ALL)
    return [
        SequenceRecord(
            Species(row.common_name, row.scientific_name, int(row.taxonomy_id)),
            row.sequence,
        )
        for row in df.itertuples(index=False)
    ]


def build_distance_graph(distances: Iterable[tuple[SequenceRecord, int]]) -> nx.Graph:
    """Return a graph with edges weighted by edit distance to Human."""
    g = nx.Graph()
    g.add_node("Human")
    for rec, dist in distances:
        name = rec.species.common_name
        g.add_node(name)
        if name.lower() != "human":
            g.add_edge("Human", name, weight=dist)
    return g


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
    logger = logging.getLogger(__name__)
    logger.info("Starting pipeline")
    # 1) Fetch or use cached data
    if force_refresh or not CSV_ALL.exists():
        logger.info("Fetching sequences from UniProt")
        records = fetch_all_beta_globin_sequences()
        _save_records(records)

    records = _load_records()

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

    logger.info("Writing close species CSV to %s", CSV_CLOSE)
    df.to_csv(CSV_CLOSE, index=False)

    # 3) Distance graph
    graph = build_distance_graph(distances)
    pos = nx.spring_layout(graph, pos={"Human": (0.0, 0.0)}, fixed=["Human"])
    d = nx.json_graph.node_link_data(graph)
    json.dump(d, open(GRAPH_JSON, "w"))
    nx_vis.render_html(graph, GRAPH_HTML, pos=pos)

    # 4) Render concentric-circle HTML
    logger.info("Rendering HTML report to %s", HTML_OUT)
    return render_html(df.sort_values("hamming_distance"), HTML_OUT)
