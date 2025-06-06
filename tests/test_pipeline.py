from __future__ import annotations
from pathlib import Path

import pandas as pd
import pytest

from species_similarity import pipeline, fetch, images, config


@pytest.fixture()
def isolated_data_dirs(tmp_path, monkeypatch):
    """
    Redirect DATA_RAW / DATA_PROCESSED and pipeline CSV/HTML paths
    into a *temporary* folder so nothing leaks to the real filesystem.
    """
    raw = tmp_path / "raw"
    processed = tmp_path / "processed"
    raw.mkdir()
    processed.mkdir()

    # patch global constants
    monkeypatch.setattr(config, "DATA_RAW", raw, raising=False)
    monkeypatch.setattr(config, "DATA_PROCESSED", processed, raising=False)
    monkeypatch.setattr(pipeline, "CSV_ALL", processed / "all.csv", raising=False)
    monkeypatch.setattr(pipeline, "CSV_CLOSE", processed / "close.csv", raising=False)
    monkeypatch.setattr(pipeline, "HTML_OUT", processed / "report.html", raising=False)
    monkeypatch.setattr(pipeline, "GRAPH_HTML", processed / "graph.html", raising=False)

    return processed


def test_run_pipeline_no_network(
    monkeypatch, isolated_data_dirs, sample_uniprot_payload
):
    """
    High-level smoke test:

    *   Fetch stub returns a single record set
    *   Image API stub returns `None`
    *   Pipeline produces CSV artefacts and an HTML report
    """

    # 1) stub fetch layer to use the sample payload
    def fake_fetch():
        from species_similarity.fetch import SequenceRecord, Species

        return [
            SequenceRecord(
                Species("Human", "Homo sapiens", 9606),
                "ACGT",
            ),
            SequenceRecord(
                Species("Mouse", "Mus musculus", 10090),
                "ACGA",
            ),
        ]

    monkeypatch.setattr(
        fetch, "fetch_all_beta_globin_sequences", fake_fetch, raising=True
    )
    monkeypatch.setattr(
        pipeline, "fetch_all_beta_globin_sequences", fake_fetch, raising=True
    )

    # 2) stub image resolution
    monkeypatch.setattr(images, "image_url", lambda *_: None, raising=True)

    # 3) run
    html_out: Path = pipeline.run(force_refresh=True)

    # 4) assertions
    assert html_out.exists()
    assert html_out.suffix == ".html"
    assert (isolated_data_dirs / "all.csv").exists()
    assert (isolated_data_dirs / "close.csv").exists()
    assert (isolated_data_dirs / "graph.html").exists()

    # spot-check CSV content
    df = pd.read_csv(isolated_data_dirs / "close.csv")
    print(df.head())
    assert set(df["scientific_name"]) == {"Homo sapiens", "Mus musculus"}
