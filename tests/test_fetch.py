from __future__ import annotations

from types import SimpleNamespace
import json
from species_similarity import fetch


class _DummyResponse(SimpleNamespace):
    """
    Stand-in for `requests.Response` that satisfies only the attributes
    `json()` and `headers` and a no-op `raise_for_status()`.
    """

    def json(self):
        return self._payload

    def raise_for_status(self):
        pass


def test_fetch_all_beta_globin_sequences(monkeypatch, sample_uniprot_payload):
    """Ensure the fetch layer converts the UniProt payload into SequenceRecords."""

    # ――― 1) stub requests.get so **no real HTTP** occurs
    def fake_get(url: str, timeout: int = 30):
        return _DummyResponse(
            _payload=sample_uniprot_payload,
            headers={},  # no “next” link → single page
        )

    monkeypatch.setattr(
        fetch,
        "requests",
        SimpleNamespace(get=fake_get),  # attribute value
        raising=False,  # do not fail if attr was missing
    )

    # ――― 2) execute & assert
    records = fetch.fetch_all_beta_globin_sequences()
    assert {r.species.common_name for r in records} == {"Human", "Mouse"}
    assert records[0].sequence == "ACGT"
    # caching layer shouldn’t interfere
    assert all(hasattr(r, "sequence") for r in records)
