"""
tests/test_differential.py
Diferansiyel test kiti: oracle/gpower_vectors.csv ve oracle/reference_stats.csv
verilerini okuyarak motoru kâhin ile karşılaştırır.
Standart unittest uyumludur.
"""

import csv
import unittest
from pathlib import Path
from powerlab.engine.solver import run_power_analysis

WORKSPACE = Path(__file__).parent.parent
GPOWER_CSV = WORKSPACE / "oracle" / "gpower_vectors.csv"
REF_CSV = WORKSPACE / "oracle" / "reference_stats.csv"


def load_gpower_vectors():
    if not GPOWER_CSV.exists():
        return []
    vectors = []
    with open(GPOWER_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("ID") or row["ID"].startswith("#"):
                continue
            if row.get("n_expected") and row["n_expected"].strip():
                vectors.append(row)
    return vectors


def load_sample_reference_vectors(limit=100):
    if not REF_CSV.exists():
        return []
    vectors = []
    with open(REF_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= limit:
                break
            vectors.append(row)
    return vectors


class TestDifferential(unittest.TestCase):
    def test_gpower_conformance_vectors(self):
        vectors = load_gpower_vectors()
        for vec in vectors:
            with self.subTest(vector_id=vec.get("ID", "vec")):
                mode = vec["mode"]
                tails = int(vec["tails"])
                dz = float(vec["dz"])
                alpha = float(vec["alpha"])
                expected_n = int(vec["n_expected"])

                params = {"tails": tails, "dz": dz, "alpha": alpha}
                if mode == "a-priori":
                    params["power"] = float(vec["power"])
                else:
                    params["n"] = int(vec["n_input"])

                res = run_power_analysis(test="t-paired", mode=mode, params=params)

                # N tam eşleşmelidir (%90 kapısı)
                self.assertEqual(
                    res["n"], expected_n,
                    f"N uyuşmazlığı ({vec['ID']}): beklenen={expected_n}, hesaplanan={res['n']}"
                )

                if vec.get("actual_power") and vec["actual_power"].strip():
                    self.assertAlmostEqual(res["actual_power"], float(vec["actual_power"]), places=3)

                if vec.get("critical_t") and vec["critical_t"].strip():
                    self.assertAlmostEqual(res["critical"], float(vec["critical_t"]), places=3)

                if vec.get("df") and vec["df"].strip():
                    self.assertEqual(res["df"], int(vec["df"]))

    def test_reference_stats_conformance(self):
        ref_vectors = load_sample_reference_vectors(limit=50)
        for ref in ref_vectors:
            with self.subTest(ref_id=ref.get("id", "ref")):
                tails = int(ref["tails"])
                dz = float(ref["dz"])
                alpha = float(ref["alpha"])
                target_power = float(ref["target_power"])
                expected_n = int(ref["n_rounded"])

                res = run_power_analysis(
                    test="t-paired",
                    mode="a-priori",
                    params={"tails": tails, "dz": dz, "alpha": alpha, "power": target_power}
                )

                self.assertEqual(
                    res["n"], expected_n,
                    f"Ref N uyuşmazlığı ({ref['id']}): beklenen={expected_n}, hesaplanan={res['n']}"
                )


if __name__ == "__main__":
    unittest.main()
