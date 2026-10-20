"""
tests/test_json_contract.py
t-paired JSON çıktısının alanları ve sırası (CONTRACT_ASSUMED.md J1-J3):
n, n_total, actual_power, critical, df, ncp — fazladan alan yok, n == n_total.
"""

import json

import pytest

from powerlab import cli
from powerlab.mcp_server import call_tool

T_PAIRED_FIELDS = ["n", "n_total", "actual_power", "critical", "df", "ncp"]

CASES = {
    "a-priori": {"mode": "a-priori", "tails": 2, "dz": 0.5, "alpha": 0.05, "power": 0.95},
    "post-hoc": {"mode": "post-hoc", "tails": 2, "dz": 0.5, "alpha": 0.05, "n": 54},
}


def _cli_args(case):
    args = ["--test", "t-paired"]
    for key, value in case.items():
        args += [f"--{key}", str(value)]
    return args


@pytest.mark.parametrize("name", CASES)
def test_cli_field_order(capsys, name):
    with pytest.raises(SystemExit) as exc:
        cli.main(_cli_args(CASES[name]))
    assert exc.value.code == 0
    data = json.loads(capsys.readouterr().out)
    assert list(data) == T_PAIRED_FIELDS
    assert data["n"] == data["n_total"]


@pytest.mark.parametrize("name", CASES)
def test_mcp_field_order(name):
    res = call_tool("power_analysis", {"test": "t-paired", **CASES[name]})
    data = res["result"]
    assert list(data) == T_PAIRED_FIELDS
    assert data["n"] == data["n_total"]
