"""
tests/generate_conformance_report.py
Uyum raporunu üç AYRI bölümle üretir:
  1) G*Power kâhini (oracle/gpower_vectors.csv): beklenen değeri dolu satırlar alan alan
     karşılaştırılır (a priori: N, Df, δ, Critical t, Actual power; post hoc: Df, δ, Critical t,
     Power). Ondalıklı alanlar CSV'deki basamak sayısına kadar (test_differential.py ile aynı kural).
     Ekran görüntüsü olup beklenen değeri boş satırlar (G*Power hata verdi) ayrı listelenir.
     CONTRACT.md §5 gereği kasıtlı sapılan vektörler ayrı listelenir ve %90 kapısına katılmaz.
  2) Eğitmen protokolü (oracle/public_vectors.jsonl, CONTRACT.md §9): istek katmanı çıktısı §6 toleransıyla.
  3) Self-check (oracle/selfcheck_scipy.csv): KÂHİN DEĞİLDİR, motorla aynı algoritmadan üretilmiştir.
Çıktı: tests/report/conformance.md
"""

import csv
import json
from datetime import datetime
from pathlib import Path

from powerlab.engine.contract import handle_request
from powerlab.engine.solver import run_power_analysis

WORKSPACE = Path(__file__).parent.parent
GPOWER_CSV = WORKSPACE / "oracle" / "gpower_vectors.csv"
SELFCHECK_CSV = WORKSPACE / "oracle" / "selfcheck_scipy.csv"
PUBLIC_JSONL = WORKSPACE / "oracle" / "public_vectors.jsonl"
BONUS_CSV = WORKSPACE / "oracle" / "gpower_bonus_modes.csv"
MULTIREG_CSV = WORKSPACE / "oracle" / "gpower_multireg.csv"
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

# CONTRACT.md §5 (dz > 0) gereği kasıtlı sapma; test_differential.py ile aynı küme.
CONTRACT_DEVIATIONS = {"V21", "V26", "V37", "V41", "V43"}

KNOWN_MISMATCHES = {
    "V42": ("Bilinen uyuşmazlık: çok büyük df'de (≈ 7.8·10¹⁰) G*Power bu N'de gücü 0.8000265 gösteriyor, "
            "scipy aynı N'de hedefin altında hesaplıyor; motor hedefi daha büyük N'de buluyor "
            "(LEDGER L17, açık soru Q7). Düzeltilmedi."),
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


def _engine_response(row):
    try:
        res = run_power_analysis(test=row["family"], mode=row["mode"], params=_params(row))
    except ValueError as e:
        return f"Reddediyor ({getattr(e, 'code', 'ValueError')}): {e}"
    return (f"Hata vermeden sonuç döndürüyor: N={res['n']}, Df={res['df']}, "
            f"δ={res['ncp']}, Critical t={res['critical']}, power={res['actual_power']}")


def _gpower_summary(row):
    n = f"N={row['n_expected']}, " if row["n_expected"] else ""
    return (f"{n}Df={row['df_expected']}, δ={row['ncp_expected']}, Critical t={row['critical_expected']}, "
            f"power={row['actual_power_expected']}")


def run_gpower_oracle():
    """Dönüş: (karşılaştırılan vektör, tam eşleşen vektör, alan uyuşmazlıkları, G*Power hata vektörleri,
    sözleşme gereği kasıtlı sapmalar)."""
    total, matches, mismatches, gpower_errors, deviations = 0, 0, [], [], []
    if not GPOWER_CSV.exists():
        return total, matches, mismatches, gpower_errors, deviations
    with open(GPOWER_CSV, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if not _has_expectation(row):
                if (row.get("screenshot") or "").strip():
                    gpower_errors.append((row["id"], row["mode"], _inputs(row), _gpower_message(row),
                                          _engine_response(row)))
                continue
            if row["id"] in CONTRACT_DEVIATIONS:
                deviations.append((row["id"], row["mode"], _inputs(row), _gpower_summary(row), _engine_response(row)))
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
                    reason = KNOWN_MISMATCHES.get(row["id"], "İncelenecek")
                    mismatches.append((row["id"], row["mode"], label, text, res[key], reason))
            matches += ok
    return total, matches, mismatches, gpower_errors, deviations


def run_public_vectors():
    """Dönüş: [(id, durum, ayrıntı)]. Karşılaştırma CONTRACT.md §6."""
    rows = []
    for line in PUBLIC_JSONL.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        vec = json.loads(line)
        payload, exit_code = handle_request(vec["input"])
        if exit_code != 0:
            rows.append((vec["id"], payload.get("code"), payload.get("error")))
            continue
        bad = []
        for key, expected in vec["expected"].items():
            got = payload.get(key)
            if isinstance(expected, int):
                ok = got == expected
            else:
                diff = abs(got - expected)
                ok = diff <= 1e-6 or diff <= 1e-6 * abs(expected)
            if not ok:
                bad.append(f"{key}: beklenen={expected}, hesaplanan={got}")
        rows.append((vec["id"], "UYUMLU" if not bad else "UYUŞMAZ", "; ".join(bad) or "tüm alanlar §6 toleransında"))
    return rows


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


def _deviation_table(deviations):
    if not deviations:
        return "Yok.\n"
    out = "| Vektör ID | Mod | Girdi | G*Power (kâhin, değişmedi) | Motor |\n|---|---|---|---|---|\n"
    for vid, mode, inputs, gpower, engine in deviations:
        out += f"| {vid} | {mode} | {inputs} | {gpower} | {engine} |\n"
    return out


BONUS_INPUTS = {
    "compromise": [("tails", "tails"), ("dz", "effect"), ("beta_alpha_ratio", "beta_alpha_ratio"), ("n_total", "n_input")],
    "criterion": [("tails", "tails"), ("dz", "effect"), ("power", "power"), ("n_total", "n_input")],
    "sensitivity": [("tails", "tails"), ("alpha", "alpha"), ("power", "power"), ("n_total", "n_input")],
}
BONUS_OUTPUTS = {
    "compromise": [("ncp", "ncp_expected"), ("critical_t", "critical_expected"), ("df", "df_expected"),
                   ("alpha", "alpha_expected"), ("beta", "beta_expected"), ("power", "power_expected")],
    "criterion": [("ncp", "ncp_expected"), ("critical_t", "critical_expected"), ("df", "df_expected"),
                  ("alpha", "alpha_expected")],
    "sensitivity": [("ncp", "ncp_expected"), ("critical_t", "critical_expected"), ("df", "df_expected"),
                    ("dz", "effect_expected")],
}


def run_bonus_modes():
    """t-paired bonus modları (K01–K09): her alan CSV'deki basamak sayısına kadar."""
    rows = []
    if not BONUS_CSV.exists():
        return rows
    with open(BONUS_CSV, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            mode = row["mode"]
            request = {"test": "t-paired", "mode": mode, **{k: row[c] for k, c in BONUS_INPUTS[mode]}}
            payload, code = handle_request(request)
            bad = []
            if code != 0:
                bad.append(f"hata: {payload.get('code')}")
            else:
                for name, column in BONUS_OUTPUTS[mode]:
                    text = row[column]
                    if name == "df":
                        if payload[name] != int(text):
                            bad.append(f"df {payload[name]} ≠ {text}")
                        continue
                    places = len(text.split(".", 1)[1]) if "." in text else 0
                    if abs(payload[name] - float(text)) > 0.5 * 10 ** -places + 1e-12:
                        bad.append(f"{name} {payload[name]!r} ≠ {text}")
            rows.append((row["id"], mode, "UYUMLU" if not bad else "UYUŞMAZ", "; ".join(bad) or "tüm alanlar"))
    return rows


MULTIREG_ERRORS = {"M14", "M15", "M16", "M26", "M28"}
MULTIREG_DEVIATIONS = {"M25"}


def run_multireg():
    """multireg-r2 (M01–M28): sayısal satırlar tüm alanlar; hata ve sapma satırları sözleşme koduyla."""
    rows = []
    if not MULTIREG_CSV.exists():
        return rows
    with open(MULTIREG_CSV, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            mode = row["mode"]
            request = {"test": "multireg-r2", "mode": mode, "f2": row["effect"], "alpha": row["alpha"],
                       "predictors": row["predictors"]}
            if mode == "a-priori":
                request["power"] = row["power"]
            else:
                request["n_total"] = row["n_input"]
            payload, code = handle_request(request)
            if row["id"] in MULTIREG_ERRORS:
                ok = code == 2
                rows.append((row["id"], mode, "UYUMLU" if ok else "UYUŞMAZ",
                             f"G*Power hata verdi; motor {payload.get('code')}"))
                continue
            if row["id"] in MULTIREG_DEVIATIONS:
                rows.append((row["id"], mode, "KASITLI SAPMA",
                             f"G*Power hesaplar (f² = 0); motor {payload.get('code')} (CONTRACT.md §5 f2 > 0)"))
                continue
            power_name = "actual_power" if mode == "a-priori" else "power"
            checks = [("ncp", "ncp_expected"), ("critical_f", "critical_expected"), ("df1", "df1_expected"),
                      ("df2", "df2_expected"), (power_name, "power_expected")]
            if mode == "a-priori":
                checks.append(("n_total", "n_expected"))
            bad = []
            if code != 0:
                bad.append(f"hata: {payload.get('code')}")
            else:
                for name, column in checks:
                    text = row[column]
                    if name in ("df1", "df2", "n_total"):
                        if payload[name] != int(text):
                            bad.append(f"{name} {payload[name]} ≠ {text}")
                        continue
                    places = len(text.split(".", 1)[1]) if "." in text else 0
                    if abs(payload[name] - float(text)) > 0.5 * 10 ** -places + 1e-12:
                        bad.append(f"{name} {payload[name]!r} ≠ {text}")
            rows.append((row["id"], mode, "UYUMLU" if not bad else "UYUŞMAZ", "; ".join(bad) or "tüm alanlar"))
    return rows


def _bonus_table(rows):
    if not rows:
        return "Yok.\n"
    out = "| Vektör ID | Mod | Durum | Ayrıntı |\n|---|---|---|---|\n"
    for vid, mode, status, detail in rows:
        out += f"| {vid} | {mode} | {status} | {detail} |\n"
    return out


def _public_table(rows):
    out = "| Vektör ID | Durum | Ayrıntı |\n|---|---|---|\n"
    for vid, status, detail in rows:
        out += f"| {vid} | {status} | {detail} |\n"
    return out


def main():
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    g_total, g_match, g_mis, g_err, g_dev = run_gpower_oracle()
    public = run_public_vectors()
    public_ok = sum(1 for _, status, _ in public if status == "UYUMLU")
    public_implemented = sum(1 for _, status, _ in public if status != "UNSUPPORTED")
    s_total, s_match, s_mis = run_selfcheck()
    bonus = run_bonus_modes()
    multireg = run_multireg()
    multireg_numeric = [r for r in multireg if r[0] not in MULTIREG_ERRORS | MULTIREG_DEVIATIONS]
    multireg_ok = sum(1 for r in multireg_numeric if r[2] == "UYUMLU")
    multireg_apriori = [r for r in multireg_numeric if r[1] == "a-priori"]
    multireg_apriori_ok = sum(1 for r in multireg_apriori if r[2] == "UYUMLU")
    bonus_ok = sum(1 for _, _, status, _ in bonus if status == "UYUMLU")
    planned = count_planned_vectors()

    if g_total == 0:
        gate = "⏸ ÖLÇÜLMEDİ — G*Power kâhin vektörü yok (ekran görüntüsüyle doğrulanmış değer: 0)"
    elif g_total + len(g_err) + len(g_dev) < planned:
        gate = (f"⏳ KISMİ — {g_total + len(g_err) + len(g_dev)}/{planned} planlı vektör toplandı "
                f"(şu anki oran {_rate(g_match, g_total)}); kapı kararı tüm vektörler dolunca verilir")
    elif g_match / g_total >= 0.90:
        gate = f"✅ GEÇTİ — {g_match}/{g_total} ({_rate(g_match, g_total)})"
    else:
        gate = f"❌ KALDI — {g_match}/{g_total} ({_rate(g_match, g_total)})"

    report = f"""# Uyum Raporu (Conformance Report)

**Oluşturulma Tarihi**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Test Aileleri**: `t-paired` (zorunlu), `multireg-r2` (bonus)
**%90 Kapısı (yalnızca G*Power kâhinine karşı)**: {gate}

---

## 1. G*Power Kâhini (`oracle/gpower_vectors.csv`)

| Metrik | Değer |
|---|---|
| Planlı vektör (şablon satırı) | {planned} |
| Beklenen değeri dolu, karşılaştırılan vektör | {g_total} |
| Sözleşme gereği kasıtlı sapma (orana katılmaz) | {len(g_dev)} |
| G*Power hata verdi (beklenen alanlar boş) | {len(g_err)} |
| Tüm alanları eşleşen vektör | {g_match} |
| Eşleşme oranı (hata vektörleri ve kasıtlı sapmalar hariç) | {_rate(g_match, g_total)} |

Karşılaştırılan alanlar: a priori'de N, Df, δ, Critical t, Actual power; post hoc'ta Df, δ, Critical t,
Power. N ve Df tam; diğerleri CSV'deki basamak sayısına kadar.

### 1a. Alan uyuşmazlıkları

{_gpower_table(g_mis)}
### 1b. G*Power hata verdi

Bu vektörlerde G*Power girdiyi reddetti; beklenen değer yoktur, orana katılmaz.

{_gpower_error_table(g_err)}
### 1c. Sözleşme gereği kasıtlı sapma

CONTRACT.md §5 `dz > 0` ister. G*Power negatif dz'yi ve post hoc'ta dz = 0'ı kabul edip hesap yapar
(LEDGER L13, L16); motor sözleşme gereği `OUT_OF_RANGE` döner. Eğitmene soruldu. Kâhin değerleri değişmedi;
bu vektörler %90 kapısına katılmaz.

{_deviation_table(g_dev)}
---

## 2. Eğitmen Protokolü (`oracle/public_vectors.jsonl`, CONTRACT.md §9)

Karşılaştırma CONTRACT.md §6: tam sayılar tam eşleşme; ondalıklar |fark| ≤ 1e-6 ya da göreli ≤ 1e-6.
Uygulanan: t-paired ve multireg-r2, beş modun hepsi; diğer aileler `UNSUPPORTED` döner.
**Uyumlu: {public_ok}/{public_implemented} uygulanan vektör** ({len(public)} vektörün {len(public) - public_implemented}'i `UNSUPPORTED`).

{_public_table(public)}
---

## 2b. Bonus modlar (`oracle/gpower_bonus_modes.csv`, G*Power ekran görüntüleri K01–K09)

t-paired compromise, criterion ve sensitivity (CONTRACT.md §3). Ondalıklar CSV'deki basamak sayısına kadar,
df tam eşleşme. %90 kapısı yalnızca a-priori N için tanımlıdır (CONTRACT.md §6); bu bölüm kapıya katılmaz.
**Uyumlu: {bonus_ok}/{len(bonus)}**

{_bonus_table(bonus)}
---

## 2c. multireg-r2 (`oracle/gpower_multireg.csv`, G*Power ekran görüntüleri M01–M28)

Bonus aile, CONTRACT.md §4.5. Sayısal satırlarda λ, Critical F, df1, df2, güç (a priori'de N de) CSV'deki
basamak sayısına kadar karşılaştırılır. **Sayısal: {multireg_ok}/{len(multireg_numeric)} uyumlu**
(a priori N: {multireg_apriori_ok}/{len(multireg_apriori)}). G*Power'ın hata verdiği 5 satırda motor kodlu hata
döner; M25 (post hoc f² = 0) sözleşme gereği kasıtlı sapmadır.

{_bonus_table(multireg)}
---

## 3. Self-check (`oracle/selfcheck_scipy.csv`) — KÂHİN DEĞİLDİR

Bu veri, motorla aynı algoritmanın (kesikli N araması + `scipy.stats.nct`) ayrı bir kopyasından
üretilmiştir (motor `scipy.special` kullanır; `scipy.stats` aynı özel fonksiyonları çağırır). Buradaki oran G*Power uyumu hakkında **hiçbir şey söylemez**; yalnızca motorun
bağımsız bir yeniden yazımla tutarlılığını gösterir.

| Metrik | Değer |
|---|---|
| Toplam vektör | {s_total} |
| Tam N eşleşmesi | {s_match} |
| Tam N eşleşme oranı | {_rate(s_match, s_total)} |

{_table(s_mis)}"""

    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Rapor oluşturuldu: {REPORT_MD} | G*Power: {g_match}/{g_total} (+{len(g_dev)} kasıtlı sapma) | "
          f"Public: {public_ok}/{public_implemented} | Self-check: {s_match}/{s_total}")


if __name__ == "__main__":
    main()
