"""
tests/test_cli_mcp_parity.py
CLI (ayrı süreç) ve MCP katmanlarının aynı girdide birebir aynı metni ürettiğini doğrular
(CONTRACT.md §7). 25 referans vektörünün tamamı tests/test_mcp_equivalence.py içindedir.
"""

import subprocess
import sys
import unittest

from powerlab.mcp_server import call_tool_text


def run_cli(args):
    cmd = [sys.executable, "-m", "powerlab.cli"]
    for key, value in args.items():
        cmd += [f"--{key}", str(value)]
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=".")


class TestCliMcpParity(unittest.TestCase):
    def assert_parity(self, args, exit_code):
        proc = run_cli(args)
        self.assertEqual(proc.returncode, exit_code)
        self.assertEqual(proc.stdout.strip(), call_tool_text("power_analysis", args))

    def test_apriori_parity(self):
        self.assert_parity({"test": "t-paired", "mode": "a-priori", "tails": 2,
                            "dz": 0.5, "alpha": 0.05, "power": 0.95}, 0)

    def test_posthoc_parity(self):
        self.assert_parity({"test": "t-paired", "mode": "post-hoc", "tails": 1,
                            "dz": 0.6, "alpha": 0.01, "n_total": 40}, 0)

    def test_error_parity(self):
        # A priori dz = 0: CONTRACT.md §5 (ve G*Power V25) gereği hata.
        self.assert_parity({"test": "t-paired", "mode": "a-priori", "tails": 2,
                            "dz": 0, "alpha": 0.05, "power": 0.80}, 2)


if __name__ == "__main__":
    unittest.main()
