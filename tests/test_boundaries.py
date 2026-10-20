import unittest
from powerlab.engine.solver import run_power_analysis


class TestBoundaries(unittest.TestCase):
    def test_extremely_small_effect_size(self):
        # dz = 0.01 çok büyük N gerektirir ama çözücü çökmeksizin doğru N'yi bulmalıdır
        res = run_power_analysis(
            test="t-paired",
            mode="a-priori",
            params={"tails": 2, "dz": 0.01, "alpha": 0.05, "power": 0.80}
        )
        self.assertGreater(res["n"], 50000)
        self.assertGreaterEqual(res["actual_power"], 0.80)

    def test_extremely_large_effect_size(self):
        # dz = 5.0 çok küçük N ile çözülür (N=3 ya da N=4)
        res = run_power_analysis(
            test="t-paired",
            mode="a-priori",
            params={"tails": 2, "dz": 5.0, "alpha": 0.05, "power": 0.99}
        )
        self.assertGreaterEqual(res["n"], 2)
        self.assertGreaterEqual(res["actual_power"], 0.99)

    def test_invalid_parameters_raise_value_error(self):
        invalid_list = [
            {"tails": 2, "dz": -0.5, "alpha": 0.05, "power": 0.80},
            {"tails": 2, "dz": 0.0, "alpha": 0.05, "power": 0.80},
            {"tails": 2, "dz": 0.5, "alpha": 0.0, "power": 0.80},
            {"tails": 2, "dz": 0.5, "alpha": 1.0, "power": 0.80},
            {"tails": 2, "dz": 0.5, "alpha": 0.05, "power": 0.0},
            {"tails": 2, "dz": 0.5, "alpha": 0.05, "power": 1.0},
            {"tails": 3, "dz": 0.5, "alpha": 0.05, "power": 0.80},
        ]
        for invalid_params in invalid_list:
            with self.subTest(invalid_params=invalid_params):
                with self.assertRaises(ValueError):
                    run_power_analysis(test="t-paired", mode="a-priori", params=invalid_params)

    def test_post_hoc_invalid_sample_size(self):
        with self.assertRaises(ValueError):
            run_power_analysis(
                test="t-paired",
                mode="post-hoc",
                params={"tails": 2, "dz": 0.5, "alpha": 0.05, "n": 1}
            )


if __name__ == "__main__":
    unittest.main()

