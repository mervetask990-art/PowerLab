"""
eval/generate_eval_report.py
eval/results/mcp_path.jsonl ve eval/results/gui_path.jsonl'den eval/AGENT_EVAL.md raporunu üretir:
test ailesi seçim doğruluğu, kalibrasyon, Türkçe–İngilizce karşılaştırması ve MCP–GUI token karşılaştırması.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "eval" / "results"
REPORT = ROOT / "eval" / "AGENT_EVAL.md"
BINS = ((0.9, 1.01, "0.90–1.00"), (0.75, 0.9, "0.75–0.89"), (0.0, 0.75, "< 0.75"))


def load(name):
    path = RESULTS / name
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()] if path.exists() else []


def pct(k, n):
    return f"{k}/{n} (%{100 * k / n:.0f})" if n else "—"


def main():
    mcp, gui = load("mcp_path.jsonl"), load("gui_path.jsonl")
    model = mcp[0]["model"] if mcp else "?"
    lines = [
        "# Ajan değerlendirmesi",
        "",
        f"Model: `{model}` (Gemini; sınıflandırıcı ve ajan aynı model). Set: `eval/agent_eval.jsonl` (10 kurgusal",
        "soru, Türkçe ve İngilizce). Beklenen aile, parametreler ve N / güç her soru için setin içindedir; beklenen",
        "değerler G*Power ekran görüntülerinden ya da CONTRACT.md §9'dan gelir (`tests/test_agent_eval_set.py`",
        "denetler). Ham sonuçlar: `eval/results/`. Yeniden üretim: `python eval/run_agent_eval.py`,",
        "`python eval/run_gui_comparison.py`, `python eval/generate_eval_report.py`.",
        "",
        "**Sistem 1 (test ailesi seçimi):** Jev erişimi olmadığı için yönergedeki izinle aynı etiket setine",
        "(`t2-indep`, `t-paired`, `anova-oneway`, `chi2-contingency`, `multireg-r2`, `ambiguous`, `unsupported`)",
        "JSON şemasıyla kısıtlanmış Gemini kullanıldı (`src/powerlab/agent/classifier.py`). Sınıflandırıcı sayı",
        "üretmez. Güven 0.75'in altındaysa ya da etiket `ambiguous` / `unsupported` ise karar araştırmacıya sorulur.",
        "",
        "## Sonuçlar",
        "",
    ]
    for lang, name in (("tr", "Türkçe"), ("en", "İngilizce")):
        rows = [r for r in mcp if r["lang"] == lang]
        lines += [
            f"### {name}",
            "",
            "| Soru | Beklenen aile | Seçilen (güven) | Aile doğru | Araca giden çağrı | Sonuç doğru | Token (giriş+çıkış) | Süre |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for r in rows:
            calls = "; ".join(f"{c['tool_input'].get('mode')} → " + ", ".join(
                f"{k}={c['tool_output'][k]}" for k in ("n_total", "power", "actual_power", "code") if k in c["tool_output"])
                for c in r["tool_calls"]) or "yok"
            lines.append(f"| {r['id']} | {r['expected_label']} | {r['label']} ({r['confidence']:.2f}) | "
                         f"{'✅' if r['label_correct'] else '❌'} | {calls} | {'✅' if r['result_correct'] else '❌'} | "
                         f"{r['tokens_in']}+{r['tokens_out']} | {r['seconds']} s |")
        lines.append("")

    lines += ["## Özet: doğru seçim oranı ve Türkçe–İngilizce karşılaştırması", "",
              "| Ölçüt | Türkçe | İngilizce |", "|---|---|---|"]
    by = {lang: [r for r in mcp if r["lang"] == lang] for lang in ("tr", "en")}
    lines.append("| Test ailesi doğru seçildi | " + " | ".join(
        pct(sum(r["label_correct"] for r in by[l]), len(by[l])) for l in ("tr", "en")) + " |")
    lines.append("| Uçtan uca doğru davranış (doğru hesap ya da doğru şekilde hesap yapmama) | " + " | ".join(
        pct(sum(r["result_correct"] for r in by[l]), len(by[l])) for l in ("tr", "en")) + " |")
    lines.append("| Ortalama güven | " + " | ".join(
        f"{sum(r['confidence'] for r in by[l]) / len(by[l]):.2f}" if by[l] else "—" for l in ("tr", "en")) + " |")
    lines.append("| Toplam token (giriş+çıkış) | " + " | ".join(
        f"{sum(r['tokens_in'] for r in by[l])}+{sum(r['tokens_out'] for r in by[l])}" for l in ("tr", "en")) + " |")
    lines.append("| Toplam süre | " + " | ".join(f"{sum(r['seconds'] for r in by[l]):.1f} s" for l in ("tr", "en")) + " |")

    lines += ["", "## Kalibrasyon", "",
              "Sınıflandırıcının söylediği güven ile gerçek doğruluk (iki dil birlikte, 20 seçim):", "",
              "| Güven aralığı | Seçim sayısı | Ortalama güven | Gerçekte doğru |", "|---|---|---|---|"]
    for low, high, label in BINS:
        rows = [r for r in mcp if low <= r["confidence"] < high]
        mean = f"{sum(r['confidence'] for r in rows) / len(rows):.2f}" if rows else "—"
        lines.append(f"| {label} | {len(rows)} | {mean} | {pct(sum(r['label_correct'] for r in rows), len(rows))} |")
    lines += ["", "Örneklem çok küçük (20 seçim); bu tablo kalibrasyon hakkında yalnızca kaba bir fikir verir.", ""]

    lines += ["## Token karşılaştırması: MCP yolu ve GUI yolu", "",
              "Hesap gerektiren sorular (E01–E06, Türkçe). MCP yolu: sınıflandırıcı + ajan + MCP aracı, metin.",
              "GUI yolu: aynı soru, G*Power'ın sonucu gösteren ekran görüntüsüyle (`eval/run_gui_comparison.py`).", "",
              "| Soru | MCP token | MCP süre | MCP doğru | GUI token | GUI süre | GUI doğru | GUI / MCP token |",
              "|---|---|---|---|---|---|---|---|"]
    mcp_tr = {r["id"]: r for r in by["tr"]}
    totals = [0, 0.0, 0, 0, 0.0, 0]
    for g in gui:
        m = mcp_tr.get(g["id"])
        if not m:
            continue
        mt, gt = m["tokens_in"] + m["tokens_out"], g["tokens_in"] + g["tokens_out"]
        totals = [totals[0] + mt, totals[1] + m["seconds"], totals[2] + m["result_correct"],
                  totals[3] + gt, totals[4] + g["seconds"], totals[5] + g["result_correct"]]
        lines.append(f"| {g['id']} | {mt} | {m['seconds']} s | {'✅' if m['result_correct'] else '❌'} | {gt} | "
                     f"{g['seconds']} s | {'✅' if g['result_correct'] else '❌'} | {gt / mt:.2f} |")
    n = sum(1 for g in gui if g["id"] in mcp_tr)
    if n:
        lines.append(f"| **Toplam** | **{totals[0]}** | **{totals[1]:.1f} s** | **{totals[2]}/{n}** | **{totals[3]}** | "
                     f"**{totals[4]:.1f} s** | **{totals[5]}/{n}** | **{totals[3] / totals[0]:.2f}** |")
    if n:
        per_shot = totals[3] / n
        breakeven = totals[0] / totals[3]
        lines += [
            "",
            "**Bulgu (ölçülen):** Bu ölçümde MCP yolu, tek ekran görüntüsü okumaktan **daha pahalı** çıktı "
            f"(GUI / MCP = {totals[3] / totals[0]:.2f}). Ekran görüntüsü başına ortalama {per_shot:.0f} token ölçüldü; "
            f"MCP yolunun maliyetine soru başına yaklaşık **{breakeven:.1f} ekran görüntüsünde** ulaşılır. "
            "Yönergedeki \"bir ekran görüntüsü yüzlerce, hatta binlerce token\" tahmini doğrulandı (~1.3 bin). "
            "Ama metin yolu \"birkaç token\" değil: araç çağrısının kendisi (JSON girdi ve çıktı) kısadır, ajan "
            "döngüsünün tokenlarının çoğu ise her turda yeniden gönderilen sistem talimatı ve araç şemasıdır; soru başına "
            "iki model turu ve bir sınıflandırıcı çağrısı vardır. CLI'yi doğrudan çağıran bir ajan bu sabit maliyeti "
            "ödemez.",
            "",
            "**Tahmin (ölçülmedi):** G*Power'da bir hesap en az üç ekran gerektirir (test ailesi seçimi, girdilerin "
            "girilmesi, sonuç); her tıklamadan sonra görüntü alan bir GUI ajanı için bu sayı daha yüksektir. Üç "
            f"görüntüde GUI yolu yaklaşık {3 * per_shot:.0f} token olur ve MCP yolunu geçer. Bu bir tahmindir; gerçek bir "
            "GUI ajanı bu projede çalıştırılmadı.",
        ]
    lines += [
        "",
        "**Yorum ve sınırlar:**",
        "- GUI satırı GUI yolunun **alt sınırıdır**: yalnızca sonucu gösteren tek bir ekran görüntüsünün okunması",
        "  ölçüldü. Gerçek bir GUI ajanı test ailesini seçmek, her alanı doldurmak ve \"Calculate\"e basmak için her",
        "  adımda yeni bir ekran görüntüsü alır; toplam maliyet bu tablodakinin birkaç katı olur.",
        "- MCP satırı ise üst sınıra yakındır: sınıflandırıcı çağrısını, araç şemasını taşıyan sistem talimatını ve",
        "  modelin cevabı yazdığı turu da içerir.",
        "- GUI yolunda doğru değer, ancak birisi G*Power'a girdileri doğru girdiyse ekranda vardır; okuma doğruluğu",
        "  hesabın doğruluğunu göstermez. MCP yolunda değer motordan gelir ve G*Power'a karşı ayrıca test edilir.",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Rapor yazıldı: {REPORT}")


if __name__ == "__main__":
    main()
