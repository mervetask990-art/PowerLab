"""
tests/test_reference_statsmodels.py
Motorun statsmodels (TTestPower) referansıyla tutarlılığı.

KÂHİN DEĞİLDİR: oracle/reference_statsmodels.csv bağımsız bir kütüphaneyle çapraz kontroldür;
kâhin yalnızca G*Power'dır. statsmodels a priori'de kesirli N verir, G*Power ve motor tavanını
alır (LEDGER L09); bu yüzden a priori'de tavan(kesirli N) = motor N beklenir.
Post hoc'ta güç farkı ≤ 1e-6 olmalıdır.
"""

import csv
import math
from pathlib import Path

import pytest

from powerlab.engine.solver import run_power_analysis

REFERENCE_CSV = Path(__file__).parent.parent / "oracle" / "reference_statsmodels.csv"
POWER_TOLERANCE = 1e-6


def load_reference():
    if not REFERENCE_CSV.exists():
        return []
    with open(REFERENCE_CSV, "r", encoding="utf-8") as f:
        return list(csv.DictReader(line for line in f if not line.startswith("#")))


REFERENCE = load_reference()

# Bilinen uyuşmazlıklar (oracle/README.md): statsmodels çözücüsünden; G*Power ve motor aynı N'yi veriyor.
KNOWN_STATSMODELS_FAILURES = {
    "V13": "statsmodels solve_power kök olmayan bir değer döndürüyor (2.72; o N'de güç 0.913 < 0.99); "
           "G*Power ve motor N=4",
    "V16": "statsmodels solve_power yakınsamıyor (güç = α, ConvergenceWarning, NaN); G*Power ve motor N=2",
}


def _param(ref):
    reason = KNOWN_STATSMODELS_FAILURES.get(ref["id"])
    marks = [pytest.mark.xfail(strict=True, reason=reason)] if reason else []
    return pytest.param(ref, id=ref["id"], marks=marks)


@pytest.mark.skipif(not REFERENCE, reason="oracle/reference_statsmodels.csv yok ya da boş")
@pytest.mark.parametrize("ref", [_param(r) for r in REFERENCE])
def test_engine_matches_statsmodels(ref):
    params = {"tails": int(ref["tails"]), "dz": float(ref["dz"]), "alpha": float(ref["alpha"])}
    if ref["mode"] == "a-priori":
        assert ref["sm_n_fractional"].strip(), f"statsmodels N üretmedi ({ref['id']}): {ref['sm_warnings']}"
        params["power"] = float(ref["power_input"])
        res = run_power_analysis(test="t-paired", mode="a-priori", params=params)
        n_ceil = math.ceil(float(ref["sm_n_fractional"]))
        assert n_ceil == int(ref["sm_n_ceil"])
        assert res["n"] == n_ceil, (
            f"N uyuşmazlığı ({ref['id']}): motor={res['n']}, tavan(statsmodels)={n_ceil} "
            f"(kesirli {ref['sm_n_fractional']})"
        )
    else:
        assert ref["sm_power"].strip(), f"statsmodels güç üretmedi ({ref['id']}): {ref['sm_warnings']}"
        params["n"] = int(ref["n_input"])
        res = run_power_analysis(test="t-paired", mode="post-hoc", params=params)
        diff = abs(res["actual_power"] - float(ref["sm_power"]))
        assert diff <= POWER_TOLERANCE, (
            f"Güç uyuşmazlığı ({ref['id']}): motor={res['actual_power']!r}, "
            f"statsmodels={ref['sm_power']}, fark={diff:.3e}"
        )
