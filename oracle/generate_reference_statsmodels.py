"""
oracle/generate_reference_statsmodels.py
t-paired için statsmodels.stats.power.TTestPower ile bağımsız referans tablosu üretir.

KÂHİN DEĞİLDİR. Kâhin yalnızca G*Power'dır (CLAUDE.md). Bu tablo, motorun bağımsız bir
kütüphaneyle çapraz kontrolüdür; motor (powerlab) burada içe aktarılmaz.

Girdiler: oracle/gpower_vectors.csv içinde G*Power'ın değer ürettiği (beklenen alanı dolu) ve
CONTRACT.md §5'e uygun (dz > 0) t-paired vektörleri; a priori ve post hoc.

Bilinen fark (LEDGER L09): statsmodels a priori'de kesirli N verir; G*Power tamsayı N verir
(tavan) ve gücü bu tamsayı N ile günceller. Bu yüzden tablo kesirli N'yi ve tavanını ayrı yazar;
a priori `sm_power` tavan N'deki güçtür.

Çıktı: oracle/reference_statsmodels.csv (değerler tam double, repr ile). İlk satır `#` ile başlayan
başlık yorumudur (kâhin olmadığı ve kütüphane sürümleri); okuyucular bu satırı atlar.

Bu makinede Smart App Control pandas 3.0.6 DLL'lerini engellediği için tablo proje .venv'i yerine
ayrı geçici bir venv'de (statsmodels 0.15.0 + pandas 2.2.3) üretildi; sürümler başlık satırındadır.
"""

import csv
import math
import warnings
from pathlib import Path

import numpy
import pandas
import scipy
import statsmodels
from statsmodels.stats.power import TTestPower

ORACLE = Path(__file__).parent
GPOWER_CSV = ORACLE / "gpower_vectors.csv"
OUT_CSV = ORACLE / "reference_statsmodels.csv"

EXPECTED_COLUMNS = ("n_expected", "actual_power_expected", "critical_expected", "df_expected", "ncp_expected")
COLUMNS = (
    "id", "mode", "tails", "dz", "alpha", "power_input", "n_input",
    "sm_n_fractional", "sm_n_ceil", "sm_power", "sm_warnings",
)
VERSIONS = (
    f"statsmodels {statsmodels.__version__}; scipy {scipy.__version__}; "
    f"numpy {numpy.__version__}; pandas {pandas.__version__}"
)
HEADER = (
    "# KÂHİN DEĞİLDİR: statsmodels.stats.power.TTestPower ile bağımsız çapraz kontrol (LEDGER L09). "
    f"Üretici: oracle/generate_reference_statsmodels.py; {VERSIONS}\n"
)


def select_vectors():
    with open(GPOWER_CSV, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [
        r for r in rows
        if r["family"] == "t-paired"
        and float(r["effect"]) > 0
        and any((r.get(c) or "").strip() for c in EXPECTED_COLUMNS)
    ]


def compute(row):
    dz, alpha, tails = float(row["effect"]), float(row["alpha"]), int(row["tails"])
    alternative = "two-sided" if tails == 2 else "larger"
    analysis = TTestPower()
    out = {
        "id": row["id"], "mode": row["mode"], "tails": tails, "dz": row["effect"], "alpha": row["alpha"],
        "power_input": row["power"], "n_input": row["n_input"],
        "sm_n_fractional": "", "sm_n_ceil": "", "sm_power": "", "sm_warnings": "",
    }
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            if row["mode"] == "a-priori":
                n_frac = float(analysis.solve_power(
                    effect_size=dz, nobs=None, alpha=alpha, power=float(row["power"]), alternative=alternative))
                n_ceil = math.ceil(n_frac)
                out["sm_n_fractional"] = repr(n_frac)
                out["sm_n_ceil"] = n_ceil
                out["sm_power"] = repr(float(analysis.power(
                    effect_size=dz, nobs=n_ceil, alpha=alpha, alternative=alternative)))
            else:
                out["sm_power"] = repr(float(analysis.power(
                    effect_size=dz, nobs=int(row["n_input"]), alpha=alpha, alternative=alternative)))
        except Exception as exc:  # noqa: BLE001 — hata metni tabloya aynen yazılır
            out["sm_warnings"] = f"HATA {type(exc).__name__}: {exc}"
    msgs = sorted({f"{w.category.__name__}: {w.message}" for w in caught})
    if msgs:
        out["sm_warnings"] = " | ".join(filter(None, [out["sm_warnings"], *msgs]))
    return out


def main():
    rows = [compute(r) for r in select_vectors()]
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        f.write(HEADER)
        writer = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} vektör yazıldı: {OUT_CSV} ({VERSIONS})")


if __name__ == "__main__":
    main()
