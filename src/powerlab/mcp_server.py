"""
src/powerlab/mcp_server.py
Model Context Protocol (MCP) Uyumlu Güç Analizi Sunucusu.
İnce katmandır: Araç çağrısını alır, doğrudan powerlab.engine'i çalıştırır.
Hesap mantığı KOPYALANMAZ.
"""

import json
import sys
from typing import Any, Dict

from powerlab.engine.contract import dumps, error_payload, handle_request
from powerlab.engine.errors import UNSUPPORTED
from powerlab.engine.solver import CONTRACT_MODES, CONTRACT_TESTS

TOOL_NAME = "power_analysis"

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


def handle_jsonrpc_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standart JSON-RPC 2.0 / MCP protokol yönlendiricisi.
    """
    req_id = request.get("id")
    method = request.get("method")
    params = request.get("params", {})

    if method == "tools/list":
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


def run_stdio_server():
    """Stdio üzerinden çalışan MCP sunucu döngüsü."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_jsonrpc_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    run_stdio_server()
