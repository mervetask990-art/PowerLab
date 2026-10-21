"""
tests/test_mcp_equivalence.py
CONTRACT.md §7: 25 referans vektörünün her birinde CLI stdout'u ile MCP çıktısı aynı olmalı.
MCP çıktısı CLI'nin stdout JSON'u ile aynı metindir; hata da aynı hata JSON'udur.
"""

import json
from pathlib import Path

import pytest

from powerlab import cli
from powerlab.mcp_server import call_tool_text, handle_jsonrpc_request

PUBLIC = Path(__file__).parent.parent / "oracle" / "public_vectors.jsonl"
VECTORS = [json.loads(line) for line in PUBLIC.read_text(encoding="utf-8").splitlines() if line.strip()]


def to_args(inp):
    args = []
    for key, value in inp.items():
        args += [f"--{key}", str(value)]
    return args


def cli_stdout(capsys, args):
    with pytest.raises(SystemExit) as exc:
        cli.main(args)
    out, err = capsys.readouterr()
    assert err == ""
    lines = out.strip().splitlines()
    assert len(lines) == 1
    return exc.value.code, lines[0]


@pytest.mark.parametrize("vec", VECTORS, ids=lambda v: v["id"])
def test_cli_equals_mcp(capsys, vec):
    exit_code, line = cli_stdout(capsys, to_args(vec["input"]))
    assert call_tool_text("power_analysis", vec["input"]) == line

    resp = handle_jsonrpc_request({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": "power_analysis", "arguments": vec["input"]},
    })
    assert resp["result"]["content"] == [{"type": "text", "text": line}]
    assert resp["result"]["isError"] == (exit_code != 0)


def test_tool_schema_uses_contract_field_names():
    resp = handle_jsonrpc_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    (tool,) = resp["result"]["tools"]
    assert tool["name"] == "power_analysis"
    schema = tool["inputSchema"]
    assert schema["required"] == ["test", "mode"]
    assert {"test", "mode", "tails", "dz", "alpha", "power", "n_total"} <= set(schema["properties"])
    assert not {"n", "d", "effect", "n-total"} & set(schema["properties"])
