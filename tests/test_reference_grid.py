"""
tests/test_reference_grid.py
Motorun 500'den fazla vektörlük statsmodels referans ağıyla tutarlılığı (oracle/reference_grid.csv).

KÂHİN DEĞİLDİR: ağ ölçek içindir; kâhin yalnızca G*Power'dır. A priori'de statsmodels kesirli N verir,
G*Power ve motor tavanını alır (LEDGER L09): tavan(kesirli N) = motor N beklenir. Post hoc'ta güç farkı
≤ 1e-6 olmalıdır. statsmodels çözücüsünün kendi denetimini geçemediği satırlar (sm_valid = 0) karşılaştırılmaz;
sayıları tests/report/reference_grid.md'de raporlanır.
"""

import csv
from pathlib import Path

import pytest

from powerlab.engine.solver import run_power_analysis

GRID_CSV = Path(__file__).parent.parent / "oracle" / "reference_grid.csv"
POWER_TOLERANCE = 1e-6


def load_grid():
    with open(GRID_CSV, "r", encoding="utf-8") as f:
        return list(csv.DictReader(line for line in f if not line.startswith("#")))


GRID = load_grid()
VALID = [r for r in GRID if r["sm_valid"] == "1"]


def engine(ref):
    params = {"alpha": float(ref["alpha"])}
    if ref["test"] == "t-paired":
        params.update(tails=int(ref["tails"]), dz=float(ref["effect"]))
    else:
        params.update(f2=float(ref["effect"]), predictors=int(ref["predictors"]))
    if ref["mode"] == "a-priori":
        params["power"] = float(ref["power_input"])
    else:
        params["n"] = int(ref["n_input"])
    return run_power_analysis(test=ref["test"], mode=ref["mode"], params=params)


def test_grid_has_more_than_500_vectors():
    assert len(GRID) > 500
    assert {r["test"] for r in GRID} == {"t-paired", "multireg-r2"}
    assert {r["mode"] for r in GRID} == {"a-priori", "post-hoc"}


@pytest.mark.parametrize("ref", VALID, ids=[r["id"] for r in VALID])
def test_engine_matches_statsmodels_grid(ref):
    res = engine(ref)
    if ref["mode"] == "a-priori":
        assert res["n"] == int(ref["sm_n_ceil"]), (
            f"N: motor={res['n']}, tavan(statsmodels)={ref['sm_n_ceil']} (kesirli {ref['sm_n_fractional']})")
    else:
        diff = abs(res["actual_power"] - float(ref["sm_power"]))
        assert diff <= POWER_TOLERANCE, f"güç: motor={res['actual_power']!r}, statsmodels={ref['sm_power']}"
