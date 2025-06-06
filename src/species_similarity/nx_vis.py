from __future__ import annotations

"""Simple NetworkX visualisation utilities."""

from pathlib import Path

import jinja2
import networkx as nx

__all__ = ["render_html"]

_TEMPLATE = jinja2.Template(
    """
<!DOCTYPE html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\" />
<title>Network graph</title>
<style>
  svg { background: #fff; border: 1px solid #dee2e6; }
  .edge { stroke: #666; stroke-width: 1.5; }
  .node { fill: #0d6efd; stroke: #fff; stroke-width: 1.5; }
  text { font-size: 12px; font-family: sans-serif; }
</style>
</head>
<body>
<svg width=\"{{ width }}\" height=\"{{ height }}\" viewBox=\"0 0 {{ width }} {{ height }}\">
  {% for u, v in edges %}
    <line class=\"edge\" x1=\"{{ pos[u][0] }}\" y1=\"{{ pos[u][1] }}\" x2=\"{{ pos[v][0] }}\" y2=\"{{ pos[v][1] }}\" />
  {% endfor %}
  {% for n in nodes %}
    <circle class=\"node\" cx=\"{{ pos[n][0] }}\" cy=\"{{ pos[n][1] }}\" r=\"8\" />
    <text x=\"{{ pos[n][0] }}\" y=\"{{ pos[n][1] - 12 }}\" text-anchor=\"middle\">{{ n }}</text>
  {% endfor %}
</svg>
</body>
</html>
""",
)


def _scale_positions(
    pos: dict[str, tuple[float, float]], width: int, height: int
) -> dict[str, tuple[float, float]]:
    min_x = min(x for x, _ in pos.values())
    min_y = min(y for _, y in pos.values())
    max_x = max(x for x, _ in pos.values())
    max_y = max(y for _, y in pos.values())
    span_x = max_x - min_x or 1
    span_y = max_y - min_y or 1
    scaled: dict[str, tuple[float, float]] = {}
    for node, (x, y) in pos.items():
        sx = (x - min_x) / span_x * width
        sy = (y - min_y) / span_y * height
        scaled[node] = (sx, sy)
    return scaled


def render_html(
    graph: nx.Graph,
    out_path: Path,
    size: tuple[int, int] = (600, 400),
    pos: dict[str, tuple[float, float]] | None = None,
) -> Path:
    """Render *graph* to an HTML file with an inline SVG."""
    width, height = size
    if pos is None:
        pos = nx.spring_layout(graph)
    scaled = _scale_positions(
        {str(n): (p[0], p[1]) for n, p in pos.items()}, width, height
    )
    edges = [(str(u), str(v)) for u, v in graph.edges()]
    nodes = [str(n) for n in graph.nodes()]
    html = _TEMPLATE.render(
        width=width, height=height, pos=scaled, edges=edges, nodes=nodes
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    return out_path
