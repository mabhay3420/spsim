from __future__ import annotations
from typing import List

import requests
import requests_cache
from urllib.parse import quote_plus

from .config import SequenceRecord, Species, DATA_RAW

# Cache UniProt responses ~1 day
requests_cache.install_cache(str(DATA_RAW / "uniprot_cache"), expire_after=86400)

GENE = "HBB"
UNIPROT_URL = "https://rest.uniprot.org/uniprotkb/search"


def _uniprot_query(query: str, page_size: int = 500) -> List[dict]:
    url = f"{UNIPROT_URL}?query={quote_plus(query)}&format=json&size={page_size}"
    out: List[dict] = []
    while url:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
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
    return out


def fetch_all_beta_globin_sequences() -> List[SequenceRecord]:
    """Return every sequence where gene==HBB."""
    raw = _uniprot_query(f"gene:{GENE}")
    records: List[SequenceRecord] = []
    for row in raw:
        organism = row["organism"]
        seq = row["sequence"]["value"]
        species = Species(
            common_name=organism.get("commonName", organism["scientificName"]),
            scientific_name=organism["scientificName"],
            taxonomy_id=int(organism["taxonId"]),
        )
        records.append(SequenceRecord(species, seq))
    return records
