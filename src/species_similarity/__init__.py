"""species_similarity package."""

from __future__ import annotations

import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

from . import nx_vis

__all__ = ["nx_vis"]
