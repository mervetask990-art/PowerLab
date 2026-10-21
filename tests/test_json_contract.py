"""
tests/test_json_contract.py
Motorun istek katmanı (powerlab.engine.contract.handle_request) t-paired çıktısını CONTRACT.md
§4.2'deki alanlarla, sırayla ve türlerle üretir; ondalıklar yuvarlanmaz (§2.3).
CLI ve MCP bu katmanı çağırır; aynı sözlük iki arayüzde de aynı JSON olur.
"""

import math

from powerlab.engine.contract import handle_request

APRIORI = {"test": "t-paired", "mode": "a-priori", "tails": 2, "dz": 0.5, "alpha": 0.05, "power": 0.95}
POSTHOC = {"test": "t-paired", "mode": "post-hoc", "tails": 2, "dz": 0.5, "alpha": 0.05, "n_total": 54}


def test_apriori_payload():
    payload, exit_code = handle_request(APRIORI)
    assert exit_code == 0
    assert list(payload) == ["ncp", "critical_t", "df", "n_total", "actual_power"]
    assert type(payload["df"]) is int and type(payload["n_total"]) is int
    assert (payload["n_total"], payload["df"]) == (54, 53)


def test_posthoc_payload():
    payload, exit_code = handle_request(POSTHOC)
    assert exit_code == 0
    assert list(payload) == ["ncp", "critical_t", "df", "power"]
    assert payload["df"] == 53


def test_floats_are_not_rounded():
    payload, _ = handle_request(POSTHOC)
    assert payload["ncp"] == 0.5 * math.sqrt(54)


def test_error_payload_shape():
    payload, exit_code = handle_request({**APRIORI, "dz": 0})
    assert exit_code == 2
    assert list(payload) == ["error", "code", "field"]
    assert (payload["code"], payload["field"]) == ("OUT_OF_RANGE", "dz")
