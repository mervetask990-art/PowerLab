"""
tests/test_differential.py
Diferansiyel test kiti.

1) oracle/gpower_vectors.csv: G*Power kâhini. Yalnızca beklenen değeri dolu
   (ekran görüntüsüyle doğrulanmış) satırlar test edilir. Hiç dolu satır yoksa
   test SESSİZCE GEÇMEZ, açıkça atlanır (skip).
   CONTRACT.md §5 (dz > 0) gereği G*Power'dan kasıtlı olarak sapılan vektörlerde (G*Power negatif
   dz ve post hoc dz = 0 ile hesap yapar; LEDGER L13, L16) motorun OUT_OF_RANGE vermesi beklenir.
   Kâhin değerleri değişmez; bu vektörler uyum raporunda ayrı listelenir, %90 kapısına katılmaz.
2) oracle/selfcheck_scipy.csv: KÂHİN DEĞİLDİR. Motorla aynı algoritmadan
   üretilmiş kendi kendine tutarlılık (self-check) verisidir.
"""

import csv
from pathlib import Path

import pytest

from powerlab.engine.solver import run_power_analysis

WORKSPACE = Path(__file__).parent.parent
GPOWER_CSV = WORKSPACE / "oracle" / "gpower_vectors.csv"
SELFCHECK_CSV = WORKSPACE / "oracle" / "selfcheck_scipy.csv"

EXPECTED_COLUMNS = (
    "n_expected",
    "actual_power_expected",
    "critical_expected",
    "df_expected",
    "ncp_expected",
)


def _has_expectation(row: dict) -> bool:
    return any((row.get(c) or "").strip() for c in EXPECTED_COLUMNS)


def load_gpower_vectors():
    if not GPOWER_CSV.exists():
        return []
    with open(GPOWER_CSV, "r", encoding="utf-8") as f:
        return [row for row in csv.DictReader(f) if _has_expectation(row)]


def load_selfcheck_vectors(limit=50):
    if not SELFCHECK_CSV.exists():
        return []
    with open(SELFCHECK_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row for i, row in enumerate(reader) if i < limit]


def _decimals(text: str) -> int:
    """CSV'deki değerin ondalık basamak sayısı (karşılaştırma hassasiyeti)."""
    text = text.strip()
    return len(text.split(".", 1)[1]) if "." in text else 0


def _params_from_row(row: dict) -> dict:
    params = {
        "tails": int(row["tails"]),
        "dz": float(row["effect"]),
        "alpha": float(row["alpha"]),
    }
    if row["mode"] == "a-priori":
        params["power"] = float(row["power"])
    else:
        params["n"] = int(row["n_input"])
    return params


GPOWER_VECTORS = load_gpower_vectors()

# CONTRACT.md §5 gereği kasıtlı sapma: G*Power hesaplar, sözleşme dz > 0 ister.
CONTRACT_DEVIATIONS = {"V21", "V26", "V37", "V41", "V43"}

# Bilinen uyuşmazlık: kâhin değeri değişmez, test strict xfail olarak kalır.
KNOWN_MISMATCHES = {
    "V42": "LEDGER L17, Q7: çok büyük df'de G*Power ile N farkı, nedeni bilinmiyor",
}


def _param(vec):
    reason = KNOWN_MISMATCHES.get(vec["id"])
    marks = [pytest.mark.xfail(strict=True, reason=reason)] if reason else []
    return pytest.param(vec, id=vec["id"], marks=marks)


@pytest.mark.skipif(
    not GPOWER_VECTORS,
    reason="0 G*Power vektörü — kâhin yok (oracle/gpower_vectors.csv beklenen sütunları boş)",
)
@pytest.mark.parametrize("vec", [_param(v) for v in GPOWER_VECTORS])
def test_gpower_oracle_vector(vec):
    if vec["id"] in CONTRACT_DEVIATIONS:
        with pytest.raises(ValueError) as exc:
            run_power_analysis(test=vec["family"], mode=vec["mode"], params=_params_from_row(vec))
        assert (getattr(exc.value, "code", None), getattr(exc.value, "field", None)) == ("OUT_OF_RANGE", "dz")
        return

    res = run_power_analysis(test=vec["family"], mode=vec["mode"], params=_params_from_row(vec))

    if vec["n_expected"].strip():
        assert res["n"] == int(vec["n_expected"]), f"N uyuşmazlığı ({vec['id']})"
    if vec["df_expected"].strip():
        assert res["df"] == int(vec["df_expected"])

    for col, key in (
        ("actual_power_expected", "actual_power"),
        ("critical_expected", "critical"),
        ("ncp_expected", "ncp"),
    ):
        text = vec[col]
        if text.strip():
            places = _decimals(text)
            assert round(res[key], places) == pytest.approx(float(text), abs=0.5 * 10 ** -places), (
                f"{key} uyuşmazlığı ({vec['id']}): beklenen={text}, hesaplanan={res[key]}"
            )


@pytest.mark.parametrize("ref", load_selfcheck_vectors(limit=50), ids=lambda r: r["id"])
def test_selfcheck_scipy(ref):
    """Kâhin değildir: motorun aynı algoritmanın bağımsız bir kopyasıyla tutarlılığı."""
    res = run_power_analysis(
        test="t-paired",
        mode="a-priori",
        params={
            "tails": int(ref["tails"]),
            "dz": float(ref["dz"]),
            "alpha": float(ref["alpha"]),
            "power": float(ref["target_power"]),
        },
    )
    assert res["n"] == int(ref["n_rounded"]), f"Selfcheck N uyuşmazlığı ({ref['id']})"
