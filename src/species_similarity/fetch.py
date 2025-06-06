from __future__ import annotations
from typing import List
import logging
from tqdm.auto import tqdm

import requests
import requests_cache
from urllib.parse import quote_plus

from .config import SequenceRecord, Species, DATA_RAW

# Cache UniProt responses ~1 day
requests_cache.install_cache(str(DATA_RAW / "uniprot_cache"), expire_after=86400)

GENE = "HBB"
UNIPROT_URL = "https://rest.uniprot.org/uniprotkb/search"


def _uniprot_query(query: str, page_size: int = 500) -> List[dict]:
    logger = logging.getLogger(__name__)
    url = f"{UNIPROT_URL}?query={quote_plus(query)}&format=json&size={page_size}"
    logger.info("Querying UniProt: %s", query)
    out: List[dict] = []
    with tqdm(desc="UniProt pages", unit="page", leave=False) as bar:
        while url:
            logger.debug("Requesting %s", url)
            try:
                r = requests.get(url, timeout=30)
                r.raise_for_status()
            except Exception as exc:
                logger.error("Request failed: %s", exc)
                raise
            payload = r.json()
            out.extend(payload["results"])
            url = next(
                (
                    link.split(";")[0].strip(" <>")
                    for link in r.headers.get("Link", "").split(",")
                    if 'rel="next"' in link
                ),
                None,
            )
            bar.update(1)
    return out


def fetch_all_beta_globin_sequences() -> List[SequenceRecord]:
    """Return every sequence where gene==HBB."""
    logger = logging.getLogger(__name__)
    raw = _uniprot_query(f"gene:{GENE}")
    logger.info("Converting UniProt records → SequenceRecord")
    records: List[SequenceRecord] = []
    for row in raw:
        organism = row["organism"]
        seq = row["sequence"]["value"]
        species = Species(
            common_name=organism.get("commonName", organism["scientificName"]),
            scientific_name=organism["scientificName"],
            taxonomy_id=int(organism["taxonId"]),
        )
        logger.debug("Parsed %s", species.common_name)
        records.append(SequenceRecord(species, seq))
    return records
