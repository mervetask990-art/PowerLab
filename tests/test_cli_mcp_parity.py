"""
tests/test_cli_mcp_parity.py
CLI ve MCP katmanlarının aynı girdi parametrelerinde
birebir aynı çıktıyı ürettiğini (parity) doğrular.
"""

import json
import subprocess
import sys
import unittest

from powerlab.mcp_server import call_tool


def run_cli(*args):
    cmd = [sys.executable, "-m", "powerlab.cli"] + list(args)
    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=".",
    )
    return proc


class TestCliMcpParity(unittest.TestCase):
    def test_apriori_parity(self):
        # 1. CLI çağrısı
        cli_res = run_cli(
            "--test", "t-paired",
            "--mode", "a-priori",
            "--tails", "2",
            "--dz", "0.5",
            "--alpha", "0.05",
            "--power", "0.95"
        )
        self.assertEqual(cli_res.returncode, 0)
        cli_data = json.loads(cli_res.stdout.strip())

        # 2. MCP çağrısı
        mcp_res = call_tool("power_analysis", {
            "test": "t-paired",
            "mode": "a-priori",
            "tails": 2,
            "dz": 0.5,
            "alpha": 0.05,
            "power": 0.95
        })
        self.assertIn("result", mcp_res)
        mcp_data = mcp_res["result"]

        # 3. Birebir Parity Kontrolü
        self.assertEqual(cli_data["n"], mcp_data["n"])
        self.assertEqual(cli_data["df"], mcp_data["df"])
        self.assertEqual(cli_data["ncp"], mcp_data["ncp"])
        self.assertEqual(cli_data["critical"], mcp_data["critical"])
        self.assertEqual(cli_data["actual_power"], mcp_data["actual_power"])

    def test_posthoc_parity(self):
        # 1. CLI çağrısı
        cli_res = run_cli(
            "--test", "t-paired",
            "--mode", "post-hoc",
            "--tails", "1",
            "--dz", "0.6",
            "--alpha", "0.01",
            "--n", "40"
        )
        self.assertEqual(cli_res.returncode, 0)
        cli_data = json.loads(cli_res.stdout.strip())

        # 2. MCP çağrısı
        mcp_res = call_tool("power_analysis", {
            "test": "t-paired",
            "mode": "post-hoc",
            "tails": 1,
            "dz": 0.6,
            "alpha": 0.01,
            "n": 40
        })
        self.assertIn("result", mcp_res)
        mcp_data = mcp_res["result"]

        # 3. Birebir Parity Kontrolü
        self.assertEqual(cli_data, mcp_data)

    def test_error_parity(self):
        # A priori dz = 0 durumunda ikisinin de hata üretmesi (G*Power V25)
        cli_res = run_cli(
            "--test", "t-paired",
            "--mode", "a-priori",
            "--tails", "2",
            "--dz", "0",
            "--alpha", "0.05",
            "--power", "0.80"
        )
        self.assertNotEqual(cli_res.returncode, 0)
        cli_err = json.loads(cli_res.stdout.strip())

        mcp_res = call_tool("power_analysis", {
            "test": "t-paired",
            "mode": "a-priori",
            "tails": 2,
            "dz": 0,
            "alpha": 0.05,
            "power": 0.80
        })
        self.assertIn("error", mcp_res)
        self.assertEqual(cli_err["error"], mcp_res["error"])


if __name__ == "__main__":
    unittest.main()
