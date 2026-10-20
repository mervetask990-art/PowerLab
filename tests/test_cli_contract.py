"""
tests/test_cli_contract.py
CLI sözleşmesini (Argparse -> Engine -> Tek satır JSON / Hata kodu != 0) doğrular.
"""

import json
import subprocess
import sys
import unittest


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


class TestCLIContract(unittest.TestCase):
    def test_cli_apriori_success(self):
        res = run_cli(
            "--test", "t-paired",
            "--mode", "a-priori",
            "--tails", "2",
            "--dz", "0.5",
            "--alpha", "0.05",
            "--power", "0.95"
        )
        self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")
        data = json.loads(res.stdout.strip())
        self.assertEqual(data["n"], 54)
        self.assertEqual(data["df"], 53)
        self.assertAlmostEqual(data["actual_power"], 0.950212, places=4)
        self.assertAlmostEqual(data["critical"], 2.005746, places=4)
        self.assertAlmostEqual(data["ncp"], 3.674235, places=4)

    def test_cli_posthoc_success(self):
        res = run_cli(
            "--test", "t-paired",
            "--mode", "post-hoc",
            "--tails", "2",
            "--dz", "0.5",
            "--alpha", "0.05",
            "--n", "54"
        )
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout.strip())
        self.assertEqual(data["n"], 54)
        self.assertAlmostEqual(data["actual_power"], 0.950212, places=4)

    def test_cli_invalid_parameter_exit_code(self):
        res = run_cli(
            "--test", "t-paired",
            "--mode", "a-priori",
            "--tails", "2",
            "--dz", "-0.5",
            "--alpha", "0.05",
            "--power", "0.95"
        )
        self.assertNotEqual(res.returncode, 0)
        err_data = json.loads(res.stderr.strip())
        self.assertIn("error", err_data)
        self.assertIn("dz", err_data["error"])


if __name__ == "__main__":
    unittest.main()

