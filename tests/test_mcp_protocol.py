"""
tests/test_mcp_protocol.py
Gerçek bir MCP istemcisinin akışı: initialize -> notifications/initialized -> tools/list -> tools/call.
El sıkışma olmadan Claude Code / Claude Desktop / MCP Inspector sunucuya bağlanamaz (CONTRACT.md §7).
"""

import json
import subprocess
import sys

from powerlab.mcp_server import LATEST_PROTOCOL_VERSION, TOOL_NAME, handle_jsonrpc_request

PAIRED_A_PRIORI = {"test": "t-paired", "mode": "a-priori", "tails": 1, "dz": 0.5, "alpha": 0.05, "power": 0.95}


def initialize(version):
    return handle_jsonrpc_request({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": version, "capabilities": {},
                   "clientInfo": {"name": "pytest", "version": "0"}},
    })


def test_initialize_echoes_supported_version():
    resp = initialize("2025-03-26")
    assert resp["id"] == 1
    result = resp["result"]
    assert result["protocolVersion"] == "2025-03-26"
    assert "tools" in result["capabilities"]
    assert result["serverInfo"]["name"] == "powerlab"


def test_initialize_offers_latest_for_unknown_version():
    assert initialize("1999-01-01")["result"]["protocolVersion"] == LATEST_PROTOCOL_VERSION


def test_notifications_get_no_response():
    assert handle_jsonrpc_request({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None
    assert handle_jsonrpc_request({"jsonrpc": "2.0", "method": "notifications/cancelled",
                                   "params": {"requestId": 1}}) is None


def test_ping_returns_empty_result():
    assert handle_jsonrpc_request({"jsonrpc": "2.0", "id": 7, "method": "ping"}) == \
        {"jsonrpc": "2.0", "id": 7, "result": {}}


def test_unknown_method_is_method_not_found():
    resp = handle_jsonrpc_request({"jsonrpc": "2.0", "id": 3, "method": "resources/list"})
    assert resp["error"]["code"] == -32601


def test_stdio_tolerates_utf8_bom():
    """Windows PowerShell boru hattı ilk satırın başına UTF-8 BOM ekler; el sıkışma yine okunmalı."""
    request = {"jsonrpc": "2.0", "id": 1, "method": "ping"}
    stdin = b"\xef\xbb\xbf" + json.dumps(request).encode("utf-8") + b"\n"
    proc = subprocess.run([sys.executable, "-m", "powerlab.mcp_server"], input=stdin,
                          capture_output=True, timeout=30)
    assert json.loads(proc.stdout) == {"jsonrpc": "2.0", "id": 1, "result": {}}


def test_stdio_session_end_to_end():
    """Sunucu ayrı süreçte; stdout'ta yalnızca JSON-RPC yanıtları olur, stderr boştur."""
    messages = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": LATEST_PROTOCOL_VERSION, "capabilities": {},
                    "clientInfo": {"name": "pytest", "version": "0"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
         "params": {"name": TOOL_NAME, "arguments": PAIRED_A_PRIORI}},
        "{bozuk json",
    ]
    stdin = "\n".join(m if isinstance(m, str) else json.dumps(m) for m in messages) + "\n"
    proc = subprocess.run([sys.executable, "-m", "powerlab.mcp_server"], input=stdin.encode("utf-8"),
                          capture_output=True, timeout=30)
    assert proc.returncode == 0
    assert proc.stderr == b""
    replies = [json.loads(line) for line in proc.stdout.decode("utf-8").splitlines()]

    # Bildirime yanıt yok: 5 mesaj -> 4 yanıt.
    assert [r["id"] for r in replies] == [1, 2, 3, None]
    assert replies[0]["result"]["protocolVersion"] == LATEST_PROTOCOL_VERSION
    assert replies[1]["result"]["tools"][0]["name"] == TOOL_NAME
    output = json.loads(replies[2]["result"]["content"][0]["text"])
    assert output["n_total"] == 45
    assert replies[2]["result"]["isError"] is False
    assert replies[3]["error"]["code"] == -32700
