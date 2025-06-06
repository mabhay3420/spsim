from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Final

# --- Paths -----------------------------------------------------
ROOT: Final[Path] = Path(__file__).resolve().parents[2]
DATA_RAW: Final[Path] = ROOT / "data" / "raw"
DATA_PROCESSED: Final[Path] = ROOT / "data" / "processed"
DATA_RAW.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

# --- Data classes ---------------------------------------------
@dataclass
class Species:
    common_name: str
    scientific_name: str
    taxonomy_id: int

@dataclass
class SequenceRecord:
    species: Species
    sequence: str