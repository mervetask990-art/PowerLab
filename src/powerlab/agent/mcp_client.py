"""
src/powerlab/agent/mcp_client.py
Ajanın MCP istemcisi: powerlab.mcp_server'ı ayrı süreç olarak başlatır ve stdio üzerinden JSON-RPC konuşur
(initialize -> notifications/initialized -> tools/list -> tools/call). Ajan motoru doğrudan çağırmaz (§8).
"""

import json
import subprocess
import sys
from typing import Any, Dict, List, Optional, Sequence

from powerlab.mcp_server import LATEST_PROTOCOL_VERSION, TOOL_NAME


class MCPError(Exception):
    pass


class MCPClient:
    def __init__(self, command: Optional[Sequence[str]] = None):
        self.command = list(command) if command else [sys.executable, "-m", "powerlab.mcp_server"]
        self._proc: Optional[subprocess.Popen] = None
        self._next_id = 0

    def __enter__(self) -> "MCPClient":
        self.start()
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def start(self) -> None:
        self._proc = subprocess.Popen(self.command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                      stderr=subprocess.DEVNULL)
        self._request("initialize", {"protocolVersion": LATEST_PROTOCOL_VERSION, "capabilities": {},
                                     "clientInfo": {"name": "powerlab-agent", "version": "1.0.0"}})
        self._write({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def close(self) -> None:
        if self._proc is None:
            return
        try:
            self._proc.stdin.close()
            self._proc.wait(timeout=5)
        except (OSError, subprocess.TimeoutExpired):
            self._proc.kill()
        self._proc = None

    def list_tools(self) -> List[Dict[str, Any]]:
        return self._request("tools/list", {})["tools"]

    def call(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """power_analysis çağrısı; dönen sözlük CLI'nin stdout JSON'udur (hata da aynı hata JSON'u)."""
        result = self._request("tools/call", {"name": TOOL_NAME, "arguments": arguments})
        return json.loads(result["content"][0]["text"])

    def _write(self, message: Dict[str, Any]) -> None:
        if self._proc is None:
            raise MCPError("MCP sunucusu başlatılmadı")
        self._proc.stdin.write((json.dumps(message) + "\n").encode("utf-8"))
        self._proc.stdin.flush()

    def _request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        self._next_id += 1
        self._write({"jsonrpc": "2.0", "id": self._next_id, "method": method, "params": params})
        line = self._proc.stdout.readline()
        if not line:
            raise MCPError("MCP sunucusu yanıt vermeden kapandı")
        response = json.loads(line)
        if response.get("id") != self._next_id:
            raise MCPError(f"Beklenmeyen yanıt kimliği: {response.get('id')}")
        if "error" in response:
            raise MCPError(f"{method}: {response['error'].get('message')}")
        return response["result"]
