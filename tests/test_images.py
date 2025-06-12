from __future__ import annotations

import importlib
from pathlib import Path
import sys
import types

import species_similarity.config as config


def test_install_cache_called(monkeypatch, tmp_path: Path) -> None:
    calls: dict[str, object] = {}

    def fake_install_cache(name: str, expire_after: int) -> None:
        calls["name"] = name
        calls["expire"] = expire_after

    monkeypatch.setattr(config, "DATA_RAW", tmp_path, raising=False)
    monkeypatch.setitem(
        sys.modules,
        "requests_cache",
        types.SimpleNamespace(install_cache=fake_install_cache),
    )

    images = importlib.import_module("species_similarity.images")
    importlib.reload(images)

    expected = str(tmp_path / "inat_cache")
    assert calls["name"] == expected
    assert calls["expire"] == 86400
