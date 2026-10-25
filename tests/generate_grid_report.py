"""
tests/generate_grid_report.py
oracle/reference_grid.csv (statsmodels, 516 vektör; KÂHİN DEĞİL) ile motorun karşılaştırma raporu:
tests/report/reference_grid.md. Çalıştırma: python tests/generate_grid_report.py
"""

import csv
import math
from collections import Counter
from pathlib import Path

from powerlab.engine.solver import run_power_analysis

ROOT = Path(__file__).parent.parent
GRID_CSV = ROOT / "oracle" / "reference_grid.csv"
REPORT = ROOT / "tests" / "report" / "reference_grid.md"
POWER_TOLERANCE = 1e-6


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


def main():
    with open(GRID_CSV, encoding="utf-8") as f:
        header = f.readline().strip()
        rows = list(csv.DictReader(f))

    groups = Counter((r["test"], r["mode"]) for r in rows)
    stats = {key: Counter() for key in groups}
    max_diff, fractional, examples = 0.0, 0, []
    for r in rows:
        s = stats[(r["test"], r["mode"])]
        if r["sm_valid"] != "1":
            s["invalid"] += 1
            continue
        res = engine(r)
        if r["mode"] == "a-priori":
            ok = res["n"] == int(r["sm_n_ceil"])
            n_frac = float(r["sm_n_fractional"])
            if n_frac != math.floor(n_frac):
                fractional += 1
            if len(examples) < 6 and r["test"] == "t-paired":
                examples.append((r["id"], r, n_frac, res["n"]))
        else:
            diff = abs(res["actual_power"] - float(r["sm_power"]))
            max_diff = max(max_diff, diff)
            ok = diff <= POWER_TOLERANCE
        s["match" if ok else "mismatch"] += 1

    valid = sum(s["match"] + s["mismatch"] for s in stats.values())
    match = sum(s["match"] for s in stats.values())
    a_priori = sum(s["match"] + s["mismatch"] for (t, m), s in stats.items() if m == "a-priori")
    lines = [
        "# statsmodels referans ağı (KÂHİN DEĞİL)",
        "",
        f"Kaynak: `oracle/reference_grid.csv` — {header.lstrip('# ')}",
        "",
        "Kâhin yalnızca G*Power'dır. Bu ağ, yönergedeki \"ölçek için 500'den fazla vektör\" maddesi içindir: motorun",
        "bağımsız bir kütüphaneyle geniş bir girdi aralığında tutarlı olduğunu gösterir; G*Power uyumunu göstermez",
        "(o: `tests/report/conformance.md`).",
        "",
        "| Test | Mod | Vektör | statsmodels geçersiz | Karşılaştırılan | Uyumlu | Uyumsuz |",
        "|---|---|---|---|---|---|---|",
    ]
    for (test, mode), total in sorted(groups.items()):
        s = stats[(test, mode)]
        lines.append(f"| {test} | {mode} | {total} | {s['invalid']} | {s['match'] + s['mismatch']} | "
                     f"{s['match']} | {s['mismatch']} |")
    lines += [
        f"| **Toplam** | | **{len(rows)}** | **{len(rows) - valid}** | **{valid}** | **{match}** | "
        f"**{valid - match}** |",
        "",
        "Ölçütler: a priori'de motor N = tavan(statsmodels kesirli N); post hoc'ta |güç farkı| ≤ 1e-6"
        f" (gözlenen en büyük fark: {max_diff:.2e}).",
        "",
        "## Kesirli N ve yukarı yuvarlama",
        "",
        f"statsmodels a priori'de N'yi kesirli verir: karşılaştırılan {a_priori} a priori satırından {fractional} tanesinde",
        "N tamsayı değildir. G*Power ve motor, gücü hedefe ulaştıran en küçük tamsayı N'yi verir; bu, kesirli N'nin",
        "tavanıdır (LEDGER L09). Örnekler (t-paired):",
        "",
        "| id | kuyruk | dz | α | hedef güç | statsmodels kesirli N | motor N |",
        "|---|---|---|---|---|---|---|",
    ]
    for id_, r, n_frac, n in examples:
        lines.append(f"| {id_} | {r['tails']} | {r['effect']} | {r['alpha']} | {r['power_input']} | {n_frac:.4f} | {n} |")
    lines += [
        "",
        "## statsmodels'ın geçersiz satırları",
        "",
        "- **Güç 1'e çok yakın, NaN:** çift yönlü `TTestPower.power` büyük dz·√N değerlerinde NaN döndürür.",
        "  Bu satırlar (`sm_valid = 0`) karşılaştırılmaz; motor bu girdilerde 0.9999… ya da 1.0 verir.",
        "- **`FTestPower` serbestlik derecesi takası:** statsmodels'ın eski `FTestPower` sınıfında `df_num` ve",
        "  `df_denom` yer değiştirmiştir (M17 girdisiyle güç 0.0678, kâhin 0.8429603). Ağ `FTestPowerF2` ile",
        "  üretildi; o sınıf M17, M19 ve CONTRACT.md §9 post hoc vektörüyle 7 ondalık aynıdır.",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"{REPORT}: {len(rows)} vektör, {valid} karşılaştırıldı, {match} uyumlu")


if __name__ == "__main__":
    main()
