"""
tests/test_agent_eval_set.py
Ajan değerlendirme seti (eval/agent_eval.jsonl): beklenen değerler uydurulmamalı. Her beklenen N ya da güç,
belirtilen kâhin satırıyla (G*Power ekran görüntüsü CSV'si ya da CONTRACT.md §9) aynı olmalı.
"""

import csv
import json
import re
from pathlib import Path

import pytest

from powerlab.agent.classifier import LABELS
from powerlab.mcp_server import call_tool

ROOT = Path(__file__).parent.parent
ITEMS = [json.loads(l) for l in (ROOT / "eval" / "agent_eval.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
PUBLIC = {v["id"]: v for v in map(json.loads, (ROOT / "oracle" / "public_vectors.jsonl").read_text(encoding="utf-8").splitlines())}


def csv_rows(name):
    with open(ROOT / "oracle" / name, encoding="utf-8") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


GPOWER = {**csv_rows("gpower_vectors.csv"), **csv_rows("gpower_multireg.csv")}


def test_ten_questions_with_both_languages():
    assert len(ITEMS) == 10
    assert all(i["tr"] and i["en"] and i["expected_label"] in LABELS for i in ITEMS)
    assert {i["expected_label"] for i in ITEMS} >= {"t-paired", "multireg-r2", "ambiguous", "unsupported"}


@pytest.mark.parametrize("item", [i for i in ITEMS if i["expected_value"] is not None], ids=lambda i: i["id"])
def test_expected_value_comes_from_oracle(item):
    match = re.search(r"\b([VM]\d\d)\b", item["source"])
    if match:
        row = GPOWER[match.group(1)]
        column = "n_expected" if item["expected_field"] == "n_total" else (
            "actual_power_expected" if "actual_power_expected" in row else "power_expected")
        assert row[column] == str(item["expected_value"]) or float(row[column]) == item["expected_value"]
        assert (ROOT / item["screenshot"]).exists()
    else:
        public_id = re.search(r"§9 (\S+)", item["source"]).group(1)
        assert PUBLIC[public_id]["expected"][item["expected_field"]] == item["expected_value"]


@pytest.mark.parametrize("item", [i for i in ITEMS if i["expected_input"]], ids=lambda i: i["id"])
def test_expected_input_reproduces_oracle_value_through_mcp(item):
    output = call_tool("power_analysis", item["expected_input"])
    assert round(output[item["expected_field"]], 7) == item["expected_value"]
