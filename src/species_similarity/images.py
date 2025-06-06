from __future__ import annotations
from functools import lru_cache
from typing import Final

# mypy: ignore-errors
from pyinaturalist.rest_api import get_observations
# from pyinaturalist import get_observations

IMAGE_SIZE: Final[str] = "medium"

@lru_cache(maxsize=None)
def image_url(scientific_name: str) -> str | None:
    try:
        rsp = get_observations(taxon_name=scientific_name, per_page=1)
        return rsp[0]["photos"][0][f"{IMAGE_SIZE}_url"]  # type: ignore[index]
    except Exception:
        return None