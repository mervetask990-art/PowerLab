"""
src/powerlab/mcp_server.py
Model Context Protocol (MCP) Uyumlu Güç Analizi Sunucusu.
İnce katmandır: Araç çağrısını alır, doğrudan powerlab.engine'i çalıştırır.
Hesap mantığı KOPYALANMAZ.
"""

import json
import sys
from typing import Dict, Any, Optional

from powerlab.engine.solver import run_power_analysis


# MCP Araç Şeması (README ve LLM Tool Calling için standart tanımlama)
POWER_ANALYSIS_TOOL_SCHEMA = {
    "name": "power_analysis",
    "description": "G*Power uyumlu istatistiksel güç ve örneklem boyutu analizi aracı.",
    "parameters": {
        "type": "object",
        "properties": {
            "test": {
                "type": "string",
                "description": "Test ailesi (örn: 't-paired', 't2-indep', 'anova-oneway')",
                "enum": ["t-paired", "t2-indep", "anova-oneway", "chi2-contingency", "multireg-r2"]
            },
            "mode": {
                "type": "string",
                "description": "Analiz türü: 'a-priori' (gereken N) veya 'post-hoc' (elde edilen güç)",
                "enum": ["a-priori", "post-hoc"],
                "default": "a-priori"
            },
            "tails": {
                "type": "integer",
                "description": "Kuyruk sayısı: 1 (tek yönlü) veya 2 (çift yönlü)",
                "enum": [1, 2],
                "default": 2
            },
            "dz": {
                "type": "number",
                "description": "Eşleştirilmiş t-testi etki büyüklüğü (Cohen's dz > 0)"
            },
            "d": {
                "type": "number",
                "description": "Genel etki büyüklüğü d (dz yerine de kabul edilir)"
            },
            "alpha": {
                "type": "number",
                "description": "Tip I hata olasılığı (örn: 0.05)",
                "default": 0.05
            },
            "power": {
                "type": "number",
                "description": "Hedef güç (1 - beta, örn: 0.80 veya 0.95, a-priori için zorunlu)"
            },
            "n": {
                "type": "integer",
                "description": "Örneklem büyüklüğü (post-hoc analizi için çift sayısı)"
            },
            "ratio": {
                "type": "number",
                "description": "İki bağımsız grup arasındaki oran (n2/n1)",
                "default": 1.0
            }
        },
        "required": ["test", "alpha"]
    }
}


def call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    MCP tool handler: Girdileri alır, engine'e devreder ve JSON uyumlu yanıt döner.
    """
    if name != "power_analysis":
        return {"error": f"Bilinmeyen araç: '{name}'"}

    test = arguments.get("test")
    mode = arguments.get("mode", "a-priori")
    # Tür dönüşümü ve doğrulama motorda yapılır (NaN/inf dahil); burada yalnızca aktarılır.
    tails = arguments.get("tails", 2)
    alpha = arguments.get("alpha", 0.05)

    params: Dict[str, Any] = {
        "tails": tails,
        "alpha": alpha,
    }

    # dz veya d
    dz_val = arguments.get("dz", arguments.get("d"))
    if dz_val is not None:
        params["dz"] = dz_val

    if "power" in arguments and arguments["power"] is not None:
        params["power"] = arguments["power"]

    if "n" in arguments and arguments["n"] is not None:
        params["n"] = arguments["n"]

    if "ratio" in arguments and arguments["ratio"] is not None:
        params["ratio"] = arguments["ratio"]

    try:
        # ASLA HESAP KOPYALANMAZ -> SADECE ENGINE ÇAĞRILIR
        result = run_power_analysis(test=test, mode=mode, params=params)
        return {"result": result}
    except Exception as err:
        return {"error": str(err)}


def handle_jsonrpc_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standart JSON-RPC 2.0 / MCP protokol yönlendiricisi.
    """
    req_id = request.get("id")
    method = request.get("method")
    params = request.get("params", {})

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [POWER_ANALYSIS_TOOL_SCHEMA]
            }
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})
        tool_res = call_tool(tool_name, tool_args)
        if "error" in tool_res:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32602,
                    "message": tool_res["error"]
                }
            }
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(tool_res["result"])
                    }
                ]
            }
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
