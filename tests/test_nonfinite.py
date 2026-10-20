"""
tests/test_nonfinite.py
NaN ve ±inf girdilerinin motor ve MCP katmanında açıklayıcı hata ürettiğini doğrular.
(CLI düzeyindeki karşılıkları tests/test_cli_errors.py içindedir.)
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
    with pytest.raises(ValueError, match="NaN/inf"):
        run_power_analysis(test="t-paired", mode="a-priori", params=params)


@pytest.mark.parametrize("value", NONFINITE, ids=["nan", "inf", "-inf"])
@pytest.mark.parametrize("key", ["dz", "alpha", "n"])
def test_posthoc_rejects_nonfinite(key, value):
    params = {**POSTHOC_BASE, key: value}
    with pytest.raises(ValueError, match="NaN/inf"):
        run_power_analysis(test="t-paired", mode="post-hoc", params=params)


def test_posthoc_rejects_fractional_n():
    with pytest.raises(ValueError, match="tamsayı"):
        run_power_analysis(test="t-paired", mode="post-hoc", params={**POSTHOC_BASE, "n": 30.5})


def test_missing_parameter_has_clear_message():
    params = {k: v for k, v in APRIORI_BASE.items() if k != "dz"}
    with pytest.raises(ValueError, match="Eksik parametre: 'dz'"):
        run_power_analysis(test="t-paired", mode="a-priori", params=params)


@pytest.mark.parametrize("value", NONFINITE, ids=["nan", "inf", "-inf"])
@pytest.mark.parametrize("key", ["dz", "alpha", "n"])
def test_mcp_returns_error_for_nonfinite(key, value):
    res = call_tool("power_analysis", {"test": "t-paired", "mode": "post-hoc", **POSTHOC_BASE, key: value})
    assert "error" in res
    assert "NaN/inf" in res["error"]
