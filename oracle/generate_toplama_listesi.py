"""
oracle/generate_toplama_listesi.py
oracle/TOPLAMA_LISTESI.md dosyasını oracle/gpower_vectors.csv'den üretir.
Kullanım: python oracle/generate_toplama_listesi.py .   (repo kökünden)
"""

import csv
import sys
from pathlib import Path

root = Path(sys.argv[1])
BS = chr(92)
SHOTS = BS.join(["C:", "Users", "User", "Desktop", "rea_test", "oracle", "screenshots"]) + BS
rows = list(csv.DictReader(open(root / "oracle" / "gpower_vectors.csv", encoding="utf-8")))
TAILS = {"1": "One", "2": "Two"}


def done(r):
    return "[x]" if r["screenshot"] else "[ ]"


def warn(r):
    n = r["notes"]
    return "⚠ " if ("GEÇERSİZ" in n or "negatif" in n.lower() or r["effect"] == "0") else ""


L = [
    "# G*Power Vektör Toplama Listesi (t-paired)",
    "",
    "**Test seçimi:** Test family = `t tests` → Statistical test = `Means: Difference between two dependent means (matched pairs)`",
    "",
    f"**Kayıt:** Her vektörde G*Power penceresinin tamamını (Input + Output Parameters görünür) `Vxx.png` adıyla şu klasöre kaydedin: `{SHOTS}`",
    "",
    "**Sıra:** Önce tüm A priori'ler (Bölüm 1), sonra tüm Post hoc'lar (Bölüm 2); mod yalnızca bir kez değişir. Değerleri ondalık **nokta** ile girin (V01'de böyle).",
    "",
    "**Hata/uyarı veren girdiler (⚠):** G*Power uyarı kutusu açarsa ya da hesaplamayı reddederse, ekran görüntüsünde o kutu ve girdiler birlikte görünsün. Output alanları boş kalsa da kaydedin.",
    "",
    "## 1. A priori — `A priori: Compute required sample size – given α, power, and effect size`",
    "",
    "| ✓ | ID | Type of power analysis | Tail(s) | Effect size dz | α err prob | Power (1-β err prob) | Not |",
    "|---|---|---|---|---|---|---|---|",
]
for r in [x for x in rows if x["mode"] == "a-priori"]:
    L.append(f"| {done(r)} | {r['id']} | A priori | {TAILS[r['tails']]} | {r['effect']} | {r['alpha']} | {r['power']} | {warn(r)}{r['notes']} |")
L += [
    "",
    "## 2. Post hoc — `Post hoc: Compute achieved power – given α, sample size, and effect size`",
    "",
    "| ✓ | ID | Type of power analysis | Tail(s) | Effect size dz | α err prob | Total sample size | Not |",
    "|---|---|---|---|---|---|---|---|",
]
for r in [x for x in rows if x["mode"] == "post-hoc"]:
    L.append(f"| {done(r)} | {r['id']} | Post hoc | {TAILS[r['tails']]} | {r['effect']} | {r['alpha']} | {r['n_input']} | {warn(r)}{r['notes']} |")
n_a = sum(x["mode"] == "a-priori" for x in rows)
n_p = sum(x["mode"] == "post-hoc" for x in rows)
L += [
    "",
    "---",
    "",
    f"Toplam {len(rows)} vektör: {n_a} A priori, {n_p} Post hoc. Bu liste `oracle/gpower_vectors.csv`'den üretilmiştir; "
    "girdiler CSV ile birebir aynıdır. Okuma ve onay adımları için bkz. `CLAUDE.md` → \"Kâhin vektörü işleme\".",
]
(root / "oracle" / "TOPLAMA_LISTESI.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("yazildi:", len(rows), "vektor", n_a, n_p)
