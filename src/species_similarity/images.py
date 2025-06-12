from __future__ import annotations
from functools import lru_cache
from typing import Final
import logging

import requests_cache

from .config import DATA_RAW

# mypy: ignore-errors
from pyinaturalist.rest_api import get_observations
# from pyinaturalist import get_observations

IMAGE_SIZE: Final[str] = "medium"

# Cache iNaturalist responses ~1 day
requests_cache.install_cache(str(DATA_RAW / "inat_cache"), expire_after=86400)


@lru_cache(maxsize=None)
def image_url(scientific_name: str) -> str | None:
    logger = logging.getLogger(__name__)
    try:
        logger.debug("Fetching image for %s", scientific_name)
        rsp = get_observations(taxon_name=scientific_name, per_page=1)
        return rsp[0]["photos"][0][f"{IMAGE_SIZE}_url"]  # type: ignore[index]
    except Exception as exc:
        logger.warning("Image lookup failed for %s: %s", scientific_name, exc)
        return None
