#!/usr/bin/env python
from pathlib import Path
import webbrowser
import argparse
import logging

from species_similarity.pipeline import run, DEFAULT_GENE


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    parser = argparse.ArgumentParser("species-similarity – end‑to‑end driver")
    parser.add_argument(
        "--refresh", action="store_true", help="Ignore on‑disk cache & re‑download"
    )
    parser.add_argument(
        "--gene",
        default=DEFAULT_GENE,
        help="Gene identifier to download (default: HBB)",
    )
    args = parser.parse_args()

    out: Path = run(force_refresh=args.refresh, gene=args.gene)
    print(f"\n✅  Report generated → {out}")
    webbrowser.open(out.as_uri())


if __name__ == "__main__":
    main()
