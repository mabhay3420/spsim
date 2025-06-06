#!/usr/bin/env python
from pathlib import Path
import webbrowser
import argparse

from species_similarity.pipeline import run


def main() -> None:
    parser = argparse.ArgumentParser("species-similarity – end‑to‑end driver")
    parser.add_argument(
        "--refresh", action="store_true", help="Ignore on‑disk cache & re‑download"
    )
    args = parser.parse_args()

    out: Path = run(force_refresh=args.refresh)
    print(f"\n✅  Report generated → {out}")
    webbrowser.open(out.as_uri())


if __name__ == "__main__":
    main()
