"""
tests/test_cli_contract.py
CLI sözleşmesini ayrı bir süreçte doğrular (CONTRACT.md §2): stdout'a tek satır JSON,
başarıda çıkış kodu 0, geçersiz girdide {"error","code","field"} ve çıkış kodu 2, stderr boş.
"""

import json
import subprocess
import sys
import unittest


def run_cli(*args):
    cmd = [sys.executable, "-m", "powerlab.cli"] + list(args)
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=".")


class TestCLIContract(unittest.TestCase):
    def test_cli_apriori_success(self):
        res = run_cli("--test", "t-paired", "--mode", "a-priori", "--tails", "2",
                      "--dz", "0.5", "--alpha", "0.05", "--power", "0.95")
        self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")
        self.assertEqual(res.stderr, "")
        data = json.loads(res.stdout.strip())
        self.assertEqual(data["n_total"], 54)
        self.assertEqual(data["df"], 53)
        self.assertAlmostEqual(data["actual_power"], 0.9502120, delta=1e-6)
        self.assertAlmostEqual(data["critical_t"], 2.0057460, delta=1e-6)
        self.assertAlmostEqual(data["ncp"], 3.6742346, delta=1e-6)

    def test_cli_posthoc_success(self):
        res = run_cli("--test", "t-paired", "--mode", "post-hoc", "--tails", "2",
                      "--dz", "0.5", "--alpha", "0.05", "--n_total", "54")
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout.strip())
        self.assertEqual(data["df"], 53)
        self.assertAlmostEqual(data["power"], 0.9502120, delta=1e-6)

    def test_cli_invalid_parameter_exit_code(self):
        res = run_cli("--test", "t-paired", "--mode", "a-priori", "--tails", "2",
                      "--dz", "0", "--alpha", "0.05", "--power", "0.95")
        self.assertEqual(res.returncode, 2)
        self.assertEqual(res.stderr, "")
        err_data = json.loads(res.stdout.strip())
        self.assertEqual(err_data["code"], "OUT_OF_RANGE")
        self.assertEqual(err_data["field"], "dz")


if __name__ == "__main__":
    unittest.main()
