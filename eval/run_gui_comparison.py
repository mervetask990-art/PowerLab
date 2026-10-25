"""
eval/run_gui_comparison.py
Token karşılaştırması, GUI yolu (yönerge, AI ajanı): MCP aracı yerine G*Power'ın ekran görüntüsü kullanılır.
Değerlendirme setinde hesap gerektiren sorular (E01–E06) Gemini'ye, o sorunun girdileriyle alınmış G*Power
ekran görüntüsüyle birlikte sorulur; model istenen değeri ekrandan okur.

Bu ölçüm GUI yolunun ALT SINIRIDIR: gerçek bir GUI ajanı test ailesini seçmek, alanları doldurmak ve
"Calculate"e basmak için her adımda yeni bir ekran görüntüsü alır; burada yalnızca son, sonucu gösteren tek
ekran görüntüsünün okunması ölçülür. Ekran görüntüleri oracle/screenshots/ altındaki kâhin görüntüleridir.

Sonuç: eval/results/gui_path.jsonl. Rapor: python eval/generate_eval_report.py
"""

import base64
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from powerlab.agent.config import load_settings  # noqa: E402
from powerlab.agent.gemini import GeminiModel  # noqa: E402

ITEMS = ROOT / "eval" / "agent_eval.jsonl"
OUT = ROOT / "eval" / "results" / "gui_path.jsonl"
PAUSE_SECONDS = 6

SYSTEM = """\
Sen G*Power 3.1.9.7'yi yalnızca ekran görüntüsü üzerinden kullanan bir ajansın. Hesap yapma; ekte G*Power
penceresinin ekran görüntüsü var. Soruda istenen değeri (örneklem büyüklüğü için "Total sample size",
güç için "Power (1-β err prob)" ya da "Actual power") ekrandan oku ve yalnızca sayıyı yaz.
"""

FIELD_HINT = {"n_total": "Total sample size", "power": "Power (1-β err prob)"}


def first_number(text):
    match = re.search(r"\d+(?:[.,]\d+)?", text or "")
    return float(match.group(0).replace(",", ".")) if match else None


def main():
    settings = load_settings()
    model = GeminiModel(settings.api_key, settings.model)
    items = [json.loads(l) for l in ITEMS.read_text(encoding="utf-8").splitlines() if l.strip()]
    results = []
    for item in items:
        if not item.get("expected_input"):
            continue
        image = base64.b64encode((ROOT / item["screenshot"]).read_bytes()).decode("ascii")
        question = item["tr"]
        if item["replies"]:
            question += " (Araştırmacı küçük etki için dz = 0.2 değerini onayladı.)"
        question += f" İstenen değer: {FIELD_HINT[item['expected_field']]}."
        contents = [{"role": "user", "parts": [{"text": question},
                                               {"inlineData": {"mimeType": "image/png", "data": image}}]}]
        start = time.perf_counter()
        reply = model.generate(SYSTEM, contents, [])
        seconds = time.perf_counter() - start
        value = first_number(reply.text)
        expected = item["expected_value"]
        correct = value is not None and (value == expected if item["expected_field"] == "n_total"
                                         else round(value, 7) == expected)
        results.append({
            "id": item["id"], "lang": "tr", "model": settings.model, "screenshot": item["screenshot"],
            "screenshot_bytes": (ROOT / item["screenshot"]).stat().st_size,
            "answer": reply.text, "value": value, "expected_value": expected, "result_correct": correct,
            "tokens_in": reply.tokens_in, "tokens_out": reply.tokens_out, "seconds": round(seconds, 2),
        })
        print(f"{item['id']} okunan={value} beklenen={expected} {'doğru' if correct else 'YANLIŞ'} "
              f"token={reply.tokens_in}+{reply.tokens_out} süre={seconds:.2f}s", flush=True)
        time.sleep(PAUSE_SECONDS)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{len(results)} sonuç yazıldı: {OUT}")


if __name__ == "__main__":
    main()
