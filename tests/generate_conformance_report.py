"""
tests/generate_conformance_report.py
Uyum raporunu iki AYRI bölümle üretir:
  1) G*Power kâhini (oracle/gpower_vectors.csv): yalnızca beklenen değeri dolu satırlar.
  2) Self-check (oracle/selfcheck_scipy.csv): KÂHİN DEĞİLDİR, motorla aynı algoritmadan üretilmiştir.
Çıktı: tests/report/conformance.md
"""

import csv
from datetime import datetime
from pathlib import Path
from powerlab.engine.solver import run_power_analysis

WORKSPACE = Path(__file__).parent.parent
GPOWER_CSV = WORKSPACE / "oracle" / "gpower_vectors.csv"
SELFCHECK_CSV = WORKSPACE / "oracle" / "selfcheck_scipy.csv"
REPORT_MD = WORKSPACE / "tests" / "report" / "conformance.md"

EXPECTED_COLUMNS = ("n_expected", "actual_power_expected", "critical_expected", "df_expected", "ncp_expected")

SELFCHECK_MISMATCH_REASON = (
    "Üretici betikte sol kuyruk NaN koruması yok: nct.cdf(-t_crit) NaN dönünce güç NaN olur, "
    "`NaN >= hedef` False verir ve betik N'yi gereğinden büyük seçer. Motor NaN'ı 0.0 kabul eder."
)


def run_gpower_oracle():
    total, matches, mismatches = 0, 0, []
    if not GPOWER_CSV.exists():
        return total, matches, mismatches
    with open(GPOWER_CSV, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if not row.get("n_expected", "").strip():
                continue
            total += 1
            params = {"tails": int(row["tails"]), "dz": float(row["effect"]), "alpha": float(row["alpha"])}
            if row["mode"] == "a-priori":
                params["power"] = float(row["power"])
            else:
                params["n"] = int(row["n_input"])
            expected_n = int(row["n_expected"])
            try:
                calculated_n = run_power_analysis(test=row["family"], mode=row["mode"], params=params)["n"]
            except Exception as e:
                mismatches.append((row["id"], expected_n, "HATA", str(e)))
                continue
            if calculated_n == expected_n:
                matches += 1
            else:
                mismatches.append((row["id"], expected_n, calculated_n, "İncelenecek"))
    return total, matches, mismatches


def run_selfcheck():
    total, matches, mismatches = 0, 0, []
    if not SELFCHECK_CSV.exists():
        return total, matches, mismatches
    with open(SELFCHECK_CSV, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            total += 1
            expected_n = int(row["n_rounded"])
            params = {
                "tails": int(row["tails"]),
                "dz": float(row["dz"]),
                "alpha": float(row["alpha"]),
                "power": float(row["target_power"]),
            }
            try:
                calculated_n = run_power_analysis(test="t-paired", mode="a-priori", params=params)["n"]
            except Exception as e:
                mismatches.append((row["id"], expected_n, "HATA", str(e)))
                continue
            if calculated_n == expected_n:
                matches += 1
            else:
                mismatches.append((row["id"], expected_n, calculated_n, SELFCHECK_MISMATCH_REASON))
    return total, matches, mismatches


def _rate(matches, total):
    return f"%{matches / total * 100.0:.2f}" if total else "ölçülemedi (0 vektör)"


def _table(mismatches):
    if not mismatches:
        return "Uyuşmazlık yok.\n"
    out = "| Vektör ID | Beklenen N | Hesaplanan N | Açıklama |\n|---|---|---|---|\n"
    for vid, exp, calc, reason in mismatches[:50]:
        out += f"| {vid} | {exp} | {calc} | {reason} |\n"
    return out


def main():
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    g_total, g_match, g_mis = run_gpower_oracle()
    s_total, s_match, s_mis = run_selfcheck()

    if g_total == 0:
        gate = "⏸ ÖLÇÜLMEDİ — G*Power kâhin vektörü yok (ekran görüntüsüyle doğrulanmış değer: 0)"
    elif g_match / g_total >= 0.90:
        gate = "✅ GEÇTİ"
    else:
        gate = "❌ KALDI"

    report = f"""# Uyum Raporu (Conformance Report)

**Oluşturulma Tarihi**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Test Ailesi**: `t-paired`
**%90 Kapısı (yalnızca G*Power kâhinine karşı)**: {gate}

---

## 1. G*Power Kâhini (`oracle/gpower_vectors.csv`)

| Metrik | Değer |
|---|---|
| Beklenen değeri dolu vektör | {g_total} |
| Tam N eşleşmesi | {g_match} |
| Tam N eşleşme oranı | {_rate(g_match, g_total)} |

{_table(g_mis)}
---

## 2. Self-check (`oracle/selfcheck_scipy.csv`) — KÂHİN DEĞİLDİR

Bu veri, motorla aynı algoritmanın (kesikli N araması + `scipy.stats.nct`) ayrı bir kopyasından
üretilmiştir. Buradaki oran G*Power uyumu hakkında **hiçbir şey söylemez**; yalnızca motorun
bağımsız bir yeniden yazımla tutarlılığını gösterir.

| Metrik | Değer |
|---|---|
| Toplam vektör | {s_total} |
| Tam N eşleşmesi | {s_match} |
| Tam N eşleşme oranı | {_rate(s_match, s_total)} |

{_table(s_mis)}"""

    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Rapor oluşturuldu: {REPORT_MD} | G*Power: {g_match}/{g_total} | Self-check: {s_match}/{s_total}")


if __name__ == "__main__":
    main()
