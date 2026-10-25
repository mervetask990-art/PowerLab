"""
src/powerlab/mcp_server.py
Model Context Protocol (MCP) Uyumlu Güç Analizi Sunucusu.
İnce katmandır: Araç çağrısını alır, doğrudan powerlab.engine'i çalıştırır.
Hesap mantığı KOPYALANMAZ.
"""

import json
import sys
from typing import Any, Dict, Optional

from powerlab.engine.contract import CONTRACT_VERSION, dumps, error_payload, handle_request
from powerlab.engine.errors import UNSUPPORTED
from powerlab.engine.solver import CONTRACT_MODES, CONTRACT_TESTS

TOOL_NAME = "power_analysis"
# MCP protokol sürümleri (en yenisi başta); istemci bunlardan birini isterse aynısıyla yanıt verilir.
SUPPORTED_PROTOCOL_VERSIONS = ("2025-06-18", "2025-03-26", "2024-11-05")
LATEST_PROTOCOL_VERSION = SUPPORTED_PROTOCOL_VERSIONS[0]

# MCP araç şeması: alan adları CLI ile birebir aynıdır (CONTRACT.md §7, §4.2).
POWER_ANALYSIS_TOOL_SCHEMA = {
    "name": TOOL_NAME,
    "description": "İstatistiksel güç ve örneklem büyüklüğü analizi (CONTRACT.md 1.0.0). G*Power 3.1.9.7 "
                   "davranışını referans alan bağımsız bir yeniden yazım; G*Power değildir. Şu an uygulanan: "
                   "t-paired ve multireg-r2, beş modun hepsi; diğer aileler UNSUPPORTED döner.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "test": {"type": "string", "enum": list(CONTRACT_TESTS), "description": "Test kimliği"},
            "mode": {"type": "string", "enum": list(CONTRACT_MODES), "description": "Analiz modu"},
            "tails": {"type": "integer", "enum": [1, 2], "description": "Kuyruk sayısı (t testleri)"},
            "dz": {"type": "number", "description": "Etki büyüklüğü dz (> 0)"},
            "alpha": {"type": "number", "description": "I. tip hata olasılığı (0 < α < 1)"},
            "power": {"type": "number", "description": "Hedef güç 1-β (a-priori, criterion, sensitivity)"},
            "n_total": {"type": "integer",
                        "description": "Toplam örneklem büyüklüğü, çift sayısı (post-hoc, compromise, criterion, sensitivity)"},
            "beta_alpha_ratio": {"type": "number", "description": "β/α oranı (> 0; yalnızca compromise)"},
            "f2": {"type": "number", "description": "Etki büyüklüğü f² (> 0; multireg-r2)"},
            "predictors": {"type": "integer", "description": "Yordayıcı sayısı (>= 1; multireg-r2)"},
        },
        "required": ["test", "mode"],
    },
}


def call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    MCP araç işleyicisi: CLI ile aynı istek katmanını çağırır; dönen sözlük CLI'nin stdout JSON'udur.
    Hesap ve doğrulama KOPYALANMAZ.
    """
    if name != TOOL_NAME:
        return error_payload(UNSUPPORTED, None, f"Bilinmeyen araç: '{name}'")
    payload, _ = handle_request(dict(arguments))
    return payload


def call_tool_text(name: str, arguments: Dict[str, Any]) -> str:
    """MCP metin içeriği: CLI'nin stdout satırıyla birebir aynı."""
    return dumps(call_tool(name, arguments))


def _initialize_result(params: Dict[str, Any]) -> Dict[str, Any]:
    """El sıkışma: istemcinin sürümü destekleniyorsa aynısı, değilse en yenisi önerilir (MCP yaşam döngüsü)."""
    requested = params.get("protocolVersion")
    version = requested if requested in SUPPORTED_PROTOCOL_VERSIONS else LATEST_PROTOCOL_VERSION
    return {
        "protocolVersion": version,
        "capabilities": {"tools": {"listChanged": False}},
        "serverInfo": {"name": "powerlab", "version": CONTRACT_VERSION},
    }


def handle_jsonrpc_request(request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Standart JSON-RPC 2.0 / MCP protokol yönlendiricisi.
    Bildirimlere (id'siz mesajlar) yanıt verilmez; None döner.
    """
    if "id" not in request:
        return None
    req_id = request.get("id")
    method = request.get("method")
    params = request.get("params") or {}

    if method == "initialize":
        return {"jsonrpc": "2.0", "id": req_id, "result": _initialize_result(params)}
    elif method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}
    elif method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": [POWER_ANALYSIS_TOOL_SCHEMA]}}
    elif method == "tools/call":
        payload = call_tool(params.get("name"), params.get("arguments", {}))
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": dumps(payload)}],
                "isError": "error" in payload,
            },
        }
    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": -32601,
                "message": f"Method '{method}' not found"
            }
        }


def _send(message: Dict[str, Any]) -> None:
    # json.dumps ASCII yazar; Windows konsol kod sayfasından bağımsızdır. stdout'a yalnızca JSON-RPC gider.
    sys.stdout.write(json.dumps(message) + "\n")
    sys.stdout.flush()


def run_stdio_server():
    """Stdio üzerinden çalışan MCP sunucu döngüsü (satır başına bir JSON-RPC mesajı, UTF-8)."""
    for raw in sys.stdin.buffer:
        # utf-8-sig: Windows PowerShell boru hattının eklediği BOM atlanır.
        line = raw.decode("utf-8-sig", errors="replace").strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except ValueError as e:
            _send({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": f"Parse error: {e}"}})
            continue
        if not isinstance(req, dict):
            _send({"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Invalid Request"}})
            continue
        try:
            resp = handle_jsonrpc_request(req)
        except Exception as e:  # Beklenmeyen durum; sunucu kapanmaz.
            resp = {"jsonrpc": "2.0", "id": req.get("id"),
                    "error": {"code": -32603, "message": f"Internal error: {e}"}}
        if resp is not None:
            _send(resp)


def main():
    """gpower-clone-mcp komutu: MCP istemcileri (Claude Code, Claude Desktop) bu süreci başlatır."""
    run_stdio_server()


if __name__ == "__main__":
    main()
