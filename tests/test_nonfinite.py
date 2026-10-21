"""
tests/test_nonfinite.py
NaN ve ±inf girdilerinin motor ve MCP katmanında INVALID_VALUE ürettiğini doğrular.
(CLI düzeyindeki karşılıkları tests/test_contract_cli.py ve tests/test_cli_errors.py içindedir.)
Motorun iç parametre adı "n"dir; sözleşmedeki "n_total" istek katmanında eşlenir.
"""

import math

import pytest

from powerlab.engine.solver import run_power_analysis
from powerlab.mcp_server import call_tool

NONFINITE = [math.nan, math.inf, -math.inf]

APRIORI_BASE = {"tails": 2, "dz": 0.5, "alpha": 0.05, "power": 0.80}
POSTHOC_BASE = {"tails": 2, "dz": 0.5, "alpha": 0.05, "n": 30}


@pytest.mark.parametrize("value", NONFINITE, ids=["nan", "inf", "-inf"])
@pytest.mark.parametrize("key", ["dz", "alpha", "power"])
def test_apriori_rejects_nonfinite(key, value):
    params = {**APRIORI_BASE, key: value}
    with pytest.raises(ValueError, match="NaN/inf") as exc:
        run_power_analysis(test="t-paired", mode="a-priori", params=params)
    assert getattr(exc.value, "code", None) == "INVALID_VALUE"


@pytest.mark.parametrize("value", NONFINITE, ids=["nan", "inf", "-inf"])
@pytest.mark.parametrize("key", ["dz", "alpha", "n"])
def test_posthoc_rejects_nonfinite(key, value):
    params = {**POSTHOC_BASE, key: value}
    with pytest.raises(ValueError, match="NaN/inf") as exc:
        run_power_analysis(test="t-paired", mode="post-hoc", params=params)
    assert getattr(exc.value, "code", None) == "INVALID_VALUE"


def test_posthoc_rejects_fractional_n():
    with pytest.raises(ValueError, match="tamsayı") as exc:
        run_power_analysis(test="t-paired", mode="post-hoc", params={**POSTHOC_BASE, "n": 30.5})
    assert getattr(exc.value, "code", None) == "INVALID_VALUE"


def test_missing_parameter_has_clear_message():
    params = {k: v for k, v in APRIORI_BASE.items() if k != "dz"}
    with pytest.raises(ValueError, match="Eksik parametre: 'dz'") as exc:
        run_power_analysis(test="t-paired", mode="a-priori", params=params)
    assert getattr(exc.value, "code", None) == "MISSING_PARAM"


@pytest.mark.parametrize("value", NONFINITE, ids=["nan", "inf", "-inf"])
@pytest.mark.parametrize("key", ["dz", "alpha", "n_total"])
def test_mcp_returns_error_for_nonfinite(key, value):
    args = {"test": "t-paired", "mode": "post-hoc", "tails": 2, "dz": 0.5, "alpha": 0.05, "n_total": 30}
    res = call_tool("power_analysis", {**args, key: value})
    assert (res["code"], res["field"]) == ("INVALID_VALUE", key)
