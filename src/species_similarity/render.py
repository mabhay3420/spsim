"""
HTML rendering: place *Homo sapiens* at the centre and arrange the remaining
species on concentric circles whose radii grow with their Hamming distance.

The layout is pure HTML + CSS (no JS).  Each species becomes an absolutely
positioned `<div>` inside a fixed-size square “radar” container.  Positions
are pre-computed in Python so the Jinja template only loops and prints.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Iterable

import jinja2
import pandas as pd

# --------------------------------------------------------------------------- #
#  Public API                                                                 #
# --------------------------------------------------------------------------- #
__all__ = ["render_concentric"]

# --------------------------------------------------------------------------- #
#  Template                                                                   #
# --------------------------------------------------------------------------- #

_TEMPLATE = jinja2.Template(
    """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>β-globin similarity – concentric view</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
      rel="stylesheet" />
<style>
  body { font-family: system-ui, sans-serif; padding: 2rem; text-align: center; }
  #radar {
      position: relative;
      margin: 0 auto;
      width: {{ size }}px;
      height: {{ size }}px;
      background: radial-gradient(circle at center,
                 rgba(0, 123, 255, .05) 0,
                 rgba(0, 123, 255, .05) 1px,
                 transparent 1px) repeat;
      background-size: {{ ring_spacing }}px {{ ring_spacing }}px;
      border: 2px solid #dee2e6;
      border-radius: 50%;
  }
  .species {
      position: absolute;
      transform: translate(-50%, -50%);
      white-space: nowrap;
      font-size: .9rem;
      max-width: 120px;
  }
  .species img {
      max-width: 60px;
      max-height: 60px;
      border-radius: 50%;
      display: block;
      margin: 0 auto .25rem;
  }
  .human { font-weight: 600; }
</style>
</head>
<body>
<h2 class="mb-4">β-globin similarity (Hamming distance)</h2>

<div id="radar">
  {# Human at centre #}
  <div class="species human"
       style="left: {{ center }}px; top: {{ center }}px;">
    {% if human.image_url %}<img src="{{ human.image_url }}" alt="Human">{% endif %}
    Human<br><small>(0)</small>
  </div>

  {# Other species #}
  {% for sp in others %}
    <div class="species"
         style="left: {{ sp.x }}px; top: {{ sp.y }}px;">
      {% if sp.image_url %}
        <img src="{{ sp.image_url }}" alt="{{ sp.name }}">
      {% endif %}
      {{ sp.name }}<br><small>({{ sp.dist }})</small>
    </div>
  {% endfor %}
</div>

<p class="mt-4 text-muted">
  Ring spacing&nbsp;=&nbsp;{{ ring_spacing }}px &nbsp;|&nbsp;
  0&nbsp;=&nbsp;Human
</p>
</body>
</html>
"""
)

# --------------------------------------------------------------------------- #
#  Helpers                                                                    #
# --------------------------------------------------------------------------- #


def _polar_to_cart(
    radius: float, angle_deg: float, centre: float
) -> tuple[float, float]:
    """Convert polar coordinates to screen X,Y (top-left origin)."""
    rad = math.radians(angle_deg)
    x = centre + radius * math.cos(rad)
    y = centre + radius * math.sin(rad)
    return x, y


def _prepare_positions(df: pd.DataFrame, size: int, ring_spacing: int):
    """
    Returns dicts for Jinja: *human* entry + list[*others*] with x,y coords.
    """
    # ------------------------------------------------------------------ #
    # Split                                                                   #
    # ------------------------------------------------------------------ #
    human_row = df.loc[df["name"].str.lower() == "human"].iloc[0]
    others_df = df.loc[df["name"].str.lower() != "human"].copy()

    # ------------------------------------------------------------------ #
    # Group by distance → ring index                                       #
    # ------------------------------------------------------------------ #
    rings = (
        others_df.groupby("hamming_distance", sort=True)
                .apply(lambda g: g.to_dict("records"), include_groups=False)
                .to_dict()
    )

    centre = size / 2
    others_out = []

    for ring_idx, (dist, rows) in enumerate(rings.items(), start=1):
        radius = ring_idx * ring_spacing
        step = 360 / len(rows)
        for i, row in enumerate(rows):
            angle = i * step
            x, y = _polar_to_cart(radius, angle, centre)
            row.update({"x": x, "y": y, "dist": dist})
            others_out.append(row)

    human = {
        "name": human_row["name"],
        "image_url": human_row.get("image_url", ""),
    }
    return human, others_out


# --------------------------------------------------------------------------- #
#  Public function                                                            #
# --------------------------------------------------------------------------- #


def render_concentric(
    df: pd.DataFrame | Iterable[dict],
    out_path: Path,
    size: int = 800,
    ring_spacing: int = 120,
) -> Path:
    """
    Render *df* (must include columns `name`, `hamming_distance`, `image_url`)
    to an HTML file positioned as concentric circles.

    Parameters
    ----------
    df
        Pandas DataFrame **or** iterable of dict rows.
    out_path
        Path where the HTML should be written.
    size
        Width/height of the square radar container (px).
    ring_spacing
        Distance (px) between successive rings.
    """
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)

    human, others = _prepare_positions(df, size, ring_spacing)
    html = _TEMPLATE.render(
        size=size,
        ring_spacing=ring_spacing,
        center=size / 2,
        human=human,
        others=others,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    return out_path
