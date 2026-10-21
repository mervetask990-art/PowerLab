"""
tests/generate_conformance_report.py
Uyum raporunu iki AYRI bölümle üretir:
  1) G*Power kâhini (oracle/gpower_vectors.csv): beklenen değeri dolu satırlar alan alan
     karşılaştırılır (a priori: N, Df, δ, Critical t, Actual power; post hoc: Df, δ, Critical t,
     Power). Ondalıklı alanlar CSV'deki basamak sayısına kadar (test_differential.py ile aynı kural).
     Ekran görüntüsü olup beklenen değeri boş satırlar (G*Power hata verdi) ayrı listelenir.
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

# (CSV sütunu, motor anahtarı, rapordaki ad, tamsayı mı)
FIELDS = {
    "a-priori": (
        ("n_expected", "n", "N", True),
        ("df_expected", "df", "Df", True),
        ("ncp_expected", "ncp", "δ", False),
        ("critical_expected", "critical", "Critical t", False),
        ("actual_power_expected", "actual_power", "Actual power", False),
    ),
    "post-hoc": (
        ("df_expected", "df", "Df", True),
        ("ncp_expected", "ncp", "δ", False),
        ("critical_expected", "critical", "Critical t", False),
        ("actual_power_expected", "actual_power", "Power", False),
    ),
}

SELFCHECK_MISMATCH_REASON = (
    "Üretici betikte sol kuyruk NaN koruması yok: nct.cdf(-t_crit) NaN dönünce güç NaN olur, "
    "`NaN >= hedef` False verir ve betik N'yi gereğinden büyük seçer. Motor NaN'ı 0.0 kabul eder."
)


def count_planned_vectors():
    if not GPOWER_CSV.exists():
        return 0
    with open(GPOWER_CSV, "r", encoding="utf-8") as f:
        return sum(1 for _ in csv.DictReader(f))


def _has_expectation(row):
    return any((row.get(c) or "").strip() for c in EXPECTED_COLUMNS)


def _decimals(text):
    """CSV'deki değerin ondalık basamak sayısı (karşılaştırma hassasiyeti)."""
    text = text.strip()
    return len(text.split(".", 1)[1]) if "." in text else 0


def _field_matches(text, value, is_int):
    if is_int:
        return value == int(text)
    places = _decimals(text)
    return abs(round(value, places) - float(text)) <= 0.5 * 10 ** -places


def _params(row):
    params = {"tails": int(row["tails"]), "dz": float(row["effect"]), "alpha": float(row["alpha"])}
    if row["mode"] == "a-priori":
        params["power"] = float(row["power"])
    else:
        params["n"] = int(row["n_input"])
    return params


def _inputs(row):
    tail = {"1": "One", "2": "Two"}.get(row["tails"], row["tails"])
    last = f"Power={row['power']}" if row["mode"] == "a-priori" else f"N={row['n_input']}"
    return f"{tail}, dz={row['effect']}, α={row['alpha']}, {last}"


def _gpower_message(row):
    notes = row.get("notes", "")
    marker = "Input error:"
    return notes[notes.index(marker) + len(marker):].strip() if marker in notes else "(notes'ta mesaj yok)"


def run_gpower_oracle():
    """Dönüş: (dolu vektör, tam eşleşen vektör, alan uyuşmazlıkları, G*Power hata vektörleri)."""
    total, matches, mismatches, gpower_errors = 0, 0, [], []
    if not GPOWER_CSV.exists():
        return total, matches, mismatches, gpower_errors
    with open(GPOWER_CSV, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if not _has_expectation(row):
                if (row.get("screenshot") or "").strip():
                    try:
                        res = run_power_analysis(test=row["family"], mode=row["mode"], params=_params(row))
                        engine = (f"Hata vermeden sonuç döndürüyor: N={res['n']}, Df={res['df']}, "
                                  f"δ={res['ncp']}, Critical t={res['critical']}, power={res['actual_power']}")
                    except Exception as e:
                        engine = f"Reddediyor: {e}"
                    gpower_errors.append((row["id"], row["mode"], _inputs(row), _gpower_message(row), engine))
                continue
            total += 1
            try:
                res = run_power_analysis(test=row["family"], mode=row["mode"], params=_params(row))
            except Exception as e:
                mismatches.append((row["id"], row["mode"], "—", "—", "HATA", str(e)))
                continue
            ok = True
            for col, key, label, is_int in FIELDS[row["mode"]]:
                text = (row.get(col) or "").strip()
                if text and not _field_matches(text, res[key], is_int):
                    ok = False
                    mismatches.append((row["id"], row["mode"], label, text, res[key], "İncelenecek"))
            matches += ok
    return total, matches, mismatches, gpower_errors


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


def _gpower_table(mismatches):
    if not mismatches:
        return "Uyuşmazlık yok.\n"
    out = "| Vektör ID | Mod | Alan | Beklenen (G*Power) | Hesaplanan (motor) | Açıklama |\n|---|---|---|---|---|---|\n"
    for vid, mode, label, exp, calc, reason in mismatches:
        out += f"| {vid} | {mode} | {label} | {exp} | {calc} | {reason} |\n"
    return out


def _gpower_error_table(gpower_errors):
    if not gpower_errors:
        return "Yok.\n"
    out = "| Vektör ID | Mod | Girdi | G*Power mesajı | Motor |\n|---|---|---|---|---|\n"
    for vid, mode, inputs, message, engine in gpower_errors:
        out += f"| {vid} | {mode} | {inputs} | {message} | {engine} |\n"
    return out


def main():
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    g_total, g_match, g_mis, g_err = run_gpower_oracle()
    s_total, s_match, s_mis = run_selfcheck()
    planned = count_planned_vectors()

    if g_total == 0:
        gate = "⏸ ÖLÇÜLMEDİ — G*Power kâhin vektörü yok (ekran görüntüsüyle doğrulanmış değer: 0)"
    elif g_total + len(g_err) < planned:
        gate = (f"⏳ KISMİ — {g_total + len(g_err)}/{planned} planlı vektör toplandı "
                f"(şu anki oran {_rate(g_match, g_total)}); kapı kararı tüm vektörler dolunca verilir")
    elif g_match / g_total >= 0.90:
        gate = f"✅ GEÇTİ — {g_match}/{g_total} ({_rate(g_match, g_total)})"
    else:
        gate = f"❌ KALDI — {g_match}/{g_total} ({_rate(g_match, g_total)})"

    report = f"""# Uyum Raporu (Conformance Report)

**Oluşturulma Tarihi**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Test Ailesi**: `t-paired`
**%90 Kapısı (yalnızca G*Power kâhinine karşı)**: {gate}

---

## 1. G*Power Kâhini (`oracle/gpower_vectors.csv`)

| Metrik | Değer |
|---|---|
| Planlı vektör (şablon satırı) | {planned} |
| Beklenen değeri dolu vektör | {g_total} |
| G*Power hata verdi (beklenen alanlar boş) | {len(g_err)} |
| Tüm alanları eşleşen vektör | {g_match} |
| Eşleşme oranı (hata vektörleri hariç) | {_rate(g_match, g_total)} |

Karşılaştırılan alanlar: a priori'de N, Df, δ, Critical t, Actual power; post hoc'ta Df, δ, Critical t,
Power. N ve Df tam; diğerleri CSV'deki basamak sayısına kadar.

### 1a. Alan uyuşmazlıkları

{_gpower_table(g_mis)}
### 1b. G*Power hata verdi

Bu vektörlerde G*Power girdiyi reddetti; beklenen değer yoktur, orana katılmaz.

{_gpower_error_table(g_err)}
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
