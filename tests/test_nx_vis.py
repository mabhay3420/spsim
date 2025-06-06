from __future__ import annotations

from pathlib import Path

import networkx as nx

from species_similarity import nx_vis


def test_render_html(tmp_path: Path) -> None:
    g = nx.path_graph(3)
    out = tmp_path / "graph.html"
    nx_vis.render_html(g, out)
    content = out.read_text(encoding="utf-8")
    assert "<svg" in content
    for node in g.nodes:
        assert str(node) in content
