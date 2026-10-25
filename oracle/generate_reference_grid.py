"""
oracle/generate_reference_grid.py
Ölçek için statsmodels ile 500'den fazla vektörlük bağımsız referans ağı üretir (ödev yönergesi, Kâhin).

KÂHİN DEĞİLDİR. Kâhin yalnızca G*Power'dır (CLAUDE.md). Motor (powerlab) burada içe aktarılmaz.

- t-paired: statsmodels.stats.power.TTestPower (tek yönlü = "larger", çift yönlü = "two-sided").
- multireg-r2: statsmodels.stats.power.FTestPowerF2; effect_size = f², df_num = k, df_denom = N − k − 1,
  ncc = 1, yani λ = f² · N (G*Power'ın modeli; Faul et al., 2009; LEDGER [DOK]).
  Dikkat: eski FTestPower sınıfında df_num ve df_denom yer değiştirmiş durumda; aynı girdiyle M17'de güç
  0.0678 verir (kâhin 0.8429603). FTestPowerF2 M17, M19 ve CONTRACT.md §9 post hoc ile 7 ondalık aynıdır
  (oracle/README.md).

A priori: statsmodels kesirli N verir; G*Power ve motor tamsayı N (tavan) verir (LEDGER L09). Tablo kesirli
N'yi, tavanını ve tavandaki gücü yazar. `sm_valid` sütunu statsmodels'ın kendi sonucunu yine statsmodels ile
denetler: tavan N'de güç ≥ hedef ve tavan − 1'de güç < hedef ise 1, değilse 0 (çözücü kök bulamamış).
Bu denetim motoru kullanmaz.

Çıktı: oracle/reference_grid.csv (değerler tam double, repr ile). İlk satır `#` başlık yorumudur.
Üretim (Smart App Control nedeniyle ayrı venv): pip install statsmodels==0.15.0 pandas==2.2.3
"""

import csv
import itertools
import math
import warnings
from pathlib import Path

import numpy
import pandas
import scipy
import statsmodels
from statsmodels.stats.power import FTestPowerF2, TTestPower

OUT_CSV = Path(__file__).parent / "reference_grid.csv"

COLUMNS = (
    "id", "test", "mode", "tails", "effect", "alpha", "power_input", "n_input", "predictors",
    "sm_n_fractional", "sm_n_ceil", "sm_power", "sm_valid", "sm_warnings",
)
VERSIONS = (
    f"statsmodels {statsmodels.__version__}; scipy {scipy.__version__}; "
    f"numpy {numpy.__version__}; pandas {pandas.__version__}"
)
HEADER = (
    "# KÂHİN DEĞİLDİR: statsmodels TTestPower / FTestPowerF2 ile bağımsız referans ağı (LEDGER L09). "
    f"Üretici: oracle/generate_reference_grid.py; {VERSIONS}\n"
)

# Ağ: tipik klinik değerler + sınırlara yakın değerler.
PAIRED_A_PRIORI = itertools.product((1, 2), (0.1, 0.2, 0.3, 0.5, 0.8, 1.2), (0.01, 0.05, 0.1), (0.8, 0.9, 0.95))
PAIRED_POST_HOC = itertools.product((1, 2), (0.1, 0.2, 0.5, 0.8, 1.2), (0.01, 0.05, 0.1),
                                    (5, 10, 20, 30, 50, 100, 300, 1000))
MULTIREG_A_PRIORI = itertools.product((0.02, 0.15, 0.35), (1, 2, 5, 10), (0.01, 0.05), (0.8, 0.95))
MULTIREG_POST_HOC = itertools.product((0.02, 0.15, 0.35), (1, 2, 5, 10), (0.01, 0.05), (20, 50, 100, 200, 500))


def paired_power(dz, n, alpha, tails):
    alternative = "two-sided" if tails == 2 else "larger"
    return float(TTestPower().power(effect_size=dz, nobs=n, alpha=alpha, alternative=alternative))


def multireg_power(f2, n, k, alpha):
    return float(FTestPowerF2().power(effect_size=f2, df_num=k, df_denom=n - k - 1, alpha=alpha, ncc=1))


def row(id_, test, mode, effect, alpha, **kw):
    out = dict.fromkeys(COLUMNS, "")
    out.update(id=id_, test=test, mode=mode, effect=repr(effect), alpha=repr(alpha))
    out.update({k: (repr(v) if isinstance(v, float) else v) for k, v in kw.items()})
    return out


def solve(out, solve_fraction, power_at, target, n_min):
    """Kesirli N, tavan, tavandaki güç ve statsmodels'ın kendi tutarlılığı."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            n_frac = float(solve_fraction())
            if not math.isfinite(n_frac):
                raise ValueError(f"kesirli N sonlu değil: {n_frac}")
            n_ceil = max(math.ceil(n_frac), n_min)
            power_ceil = power_at(n_ceil)
            below_ok = n_ceil - 1 < n_min or power_at(n_ceil - 1) < target
            out.update(sm_n_fractional=repr(n_frac), sm_n_ceil=n_ceil, sm_power=repr(power_ceil),
                       sm_valid=int(power_ceil >= target and below_ok))
        except Exception as exc:  # noqa: BLE001 — hata metni tabloya aynen yazılır
            out.update(sm_valid=0, sm_warnings=f"HATA {type(exc).__name__}: {exc}")
    msgs = sorted({f"{w.category.__name__}: {w.message}" for w in caught})
    if msgs:
        out["sm_warnings"] = " | ".join(filter(None, [out["sm_warnings"], *msgs]))
    return out


def generate():
    rows, i = [], 0

    def next_id():
        nonlocal i
        i += 1
        return f"G{i:04d}"

    for tails, dz, alpha, power in PAIRED_A_PRIORI:
        alt = "two-sided" if tails == 2 else "larger"
        out = row(next_id(), "t-paired", "a-priori", dz, alpha, tails=tails, power_input=power)
        rows.append(solve(out, lambda: TTestPower().solve_power(effect_size=dz, nobs=None, alpha=alpha,
                                                                 power=power, alternative=alt),
                          lambda n: paired_power(dz, n, alpha, tails), power, n_min=3))
    for tails, dz, alpha, n in PAIRED_POST_HOC:
        rows.append(post_hoc(row(next_id(), "t-paired", "post-hoc", dz, alpha, tails=tails, n_input=n),
                             paired_power(dz, n, alpha, tails)))
    for f2, k, alpha, power in MULTIREG_A_PRIORI:
        out = row(next_id(), "multireg-r2", "a-priori", f2, alpha, predictors=k, power_input=power)
        rows.append(solve(out, lambda: FTestPowerF2().solve_power(effect_size=f2, df_num=k, df_denom=None,
                                                                 alpha=alpha, power=power, ncc=1) + k + 1,
                          lambda n: multireg_power(f2, n, k, alpha), power, n_min=k + 2))
    for f2, k, alpha, n in MULTIREG_POST_HOC:
        rows.append(post_hoc(row(next_id(), "multireg-r2", "post-hoc", f2, alpha, predictors=k, n_input=n),
                             multireg_power(f2, n, k, alpha)))
    return rows


def post_hoc(out, power):
    """statsmodels güç 1'e çok yakınken NaN döndürebilir (çift yönlü TTestPower); o satır geçersiz sayılır."""
    out.update(sm_power=repr(power), sm_valid=int(math.isfinite(power)))
    if not math.isfinite(power):
        out["sm_warnings"] = "statsmodels gücü sonlu değil (NaN)"
    return out


def main():
    rows = generate()
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        f.write(HEADER)
        writer = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    invalid = sum(1 for r in rows if r["sm_valid"] == 0)
    print(f"{len(rows)} vektör yazıldı ({invalid} tanesinde statsmodels çözücüsü tutarsız): {OUT_CSV} ({VERSIONS})")


if __name__ == "__main__":
    main()
