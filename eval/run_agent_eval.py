"""
eval/run_agent_eval.py
Ajan değerlendirmesi, MCP yolu (yönerge, AI ajanı): eval/agent_eval.jsonl'deki 10 soru Türkçe ve İngilizce
olarak ajana sorulur. Ajan = sınıflandırıcı (Sistem 1) + Gemini + MCP aracı; hesap motordan gelir.

Her soru için yazılan sonuç (eval/results/mcp_path.jsonl): sınıflandırıcının etiketi ve güveni, araca giden
çağrılar, sonucun kâhinle uyumu, token ve süre. Araç çağrıları logs/agent_calls.jsonl'e de yazılır (§8).
Rapor: python eval/generate_eval_report.py

Çalıştırma (anahtar .env içinde): .\\.venv\\Scripts\\python eval\\run_agent_eval.py
Ücretsiz katmanın hız sınırına takılmamak için sorular arasında bekler.
"""

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from powerlab.agent.agent import DEFAULT_LOG, Agent  # noqa: E402
from powerlab.agent.classifier import FamilyClassifier  # noqa: E402
from powerlab.agent.config import load_settings  # noqa: E402
from powerlab.agent.gemini import GeminiModel  # noqa: E402
from powerlab.agent.mcp_client import MCPClient  # noqa: E402

ITEMS = ROOT / "eval" / "agent_eval.jsonl"
OUT = ROOT / "eval" / "results" / "mcp_path.jsonl"
LOG = ROOT / DEFAULT_LOG
PAUSE_SECONDS = 6


def same_input(actual, expected):
    if actual.keys() != expected.keys():
        return False
    return all(abs(float(actual[k]) - float(v)) < 1e-12 if isinstance(v, (int, float)) else actual[k] == v
               for k, v in expected.items())


def value_matches(output, field, expected):
    if field not in output:
        return False
    return output[field] == expected if field == "n_total" else round(output[field], 7) == expected


def run_item(item, lang, model, tools):
    before = LOG.read_text(encoding="utf-8").count("\n") if LOG.exists() else 0
    agent = Agent(model, tools, LOG, classifier=FamilyClassifier(model))
    replies = item.get("replies_en", item["replies"]) if lang == "en" else item["replies"]
    start = time.perf_counter()
    answers = [agent.ask(item[lang])]
    for reply in replies:
        answers.append(agent.ask(reply))
    seconds = time.perf_counter() - start
    lines = LOG.read_text(encoding="utf-8").splitlines()[before:] if LOG.exists() else []
    calls = [json.loads(l) for l in lines]

    first = agent.classifications[0] if agent.classifications else None
    expected_calls = item["expected_input"] is not None
    if expected_calls:
        correct = any(same_input(c["tool_input"], item["expected_input"])
                      and value_matches(c["tool_output"], item["expected_field"], item["expected_value"])
                      for c in calls)
    else:
        correct = not calls  # kapsam dışı / belirsiz / desteklenmeyen: hesap yapılmamalı
    return {
        "id": item["id"], "lang": lang, "expected_label": item["expected_label"],
        "label": first.label if first else None, "confidence": first.confidence if first else None,
        "label_correct": bool(first and first.label == item["expected_label"]),
        "asked_researcher": bool(first and first.needs_researcher),
        "tool_calls": [{"tool_input": c["tool_input"], "tool_output": c["tool_output"]} for c in calls],
        "result_correct": correct, "tokens_in": agent.tokens_in, "tokens_out": agent.tokens_out,
        "seconds": round(seconds, 2), "answers": answers,
    }


def main():
    settings = load_settings()
    model = GeminiModel(settings.api_key, settings.model)
    items = [json.loads(l) for l in ITEMS.read_text(encoding="utf-8").splitlines() if l.strip()]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    results = []
    with MCPClient() as tools:
        for lang in ("tr", "en"):
            for item in items:
                result = run_item(item, lang, model, tools)
                result["model"] = settings.model
                results.append(result)
                print(f"{item['id']} [{lang}] etiket={result['label']} ({result['confidence']}) "
                      f"sonuç={'doğru' if result['result_correct'] else 'YANLIŞ'} "
                      f"token={result['tokens_in']}+{result['tokens_out']} süre={result['seconds']}s", flush=True)
                time.sleep(PAUSE_SECONDS)
    with OUT.open("w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{len(results)} sonuç yazıldı: {OUT}")


if __name__ == "__main__":
    main()
