"""
tests/test_timing.py
CONTRACT.md §2.1: her çağrı 2 saniye içinde tamamlanmalı. Her çağrı yeni bir süreçtir (soğuk
başlatma dahil); ilk çağrı dosya önbelleği soğukken, sonrakiler ılıkken ölçülür.
"""

import subprocess
import sys
import time
from pathlib import Path

import pytest

LIMIT_SECONDS = 2.0

CASES = {
    "a-priori": ["--test", "t-paired", "--mode", "a-priori", "--tails", "1",
                 "--dz", "0.5", "--alpha", "0.05", "--power", "0.95"],
    "post-hoc": ["--test", "t-paired", "--mode", "post-hoc", "--tails", "1",
                 "--dz", "0.5", "--alpha", "0.05", "--n_total", "45"],
    "a-priori-buyuk-N": ["--test", "t-paired", "--mode", "a-priori", "--tails", "2",
                         "--dz", "0.00001", "--alpha", "0.05", "--power", "0.80"],
}


def command():
    scripts = Path(sys.executable).parent
    for candidate in (scripts / "gpower-clone.exe", scripts / "gpower-clone"):
        if candidate.exists():
            return [str(candidate)]
    return [sys.executable, "-m", "powerlab.cli"]


@pytest.mark.parametrize("name", list(CASES))
def test_call_completes_within_two_seconds(name):
    durations = []
    for _ in range(3):
        start = time.perf_counter()
        proc = subprocess.run(command() + CASES[name], capture_output=True, text=True)
        durations.append(time.perf_counter() - start)
        assert proc.returncode == 0, proc.stdout
    assert max(durations) < LIMIT_SECONDS, f"{name}: {[round(d, 3) for d in durations]} s"
