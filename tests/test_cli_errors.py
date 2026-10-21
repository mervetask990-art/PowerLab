"""
tests/test_cli_errors.py
CLI ayrı süreçte (CONTRACT.md §2.3, §2.4): her hata STDOUT'a tek satır {"error","code","field"}
yazar, geçersiz girdide çıkış kodu 2'dir ve stderr boş kalır. --help ve --version çalışır.
Kod/alan eşlemesinin tamamı tests/test_contract_cli.py içindedir.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

VALID_APRIORI = ["--test", "t-paired", "--mode", "a-priori", "--tails", "2",
                 "--dz", "0.5", "--alpha", "0.05", "--power", "0.95"]


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "powerlab.cli", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def assert_json_error(proc, code, field):
    assert proc.returncode == 2
    assert proc.stderr == "", f"stderr boş olmalı, alınan: {proc.stderr!r}"
    lines = proc.stdout.strip().splitlines()
    assert len(lines) == 1, f"tek satır JSON bekleniyordu: {proc.stdout!r}"
    payload = json.loads(lines[0])
    assert list(payload) == ["error", "code", "field"]
    assert (payload["code"], payload["field"]) == (code, field)


def test_help_still_works():
    proc = run_cli("--help")
    assert proc.returncode == 0
    assert proc.stderr == ""
    assert proc.stdout.startswith("usage: gpower-clone")
    assert "Kuyruk sayısı" in proc.stdout  # UTF-8 Türkçe karakterler bozulmadan


def test_version():
    proc = run_cli("--version")
    assert proc.returncode == 0
    assert proc.stderr == ""
    assert json.loads(proc.stdout)["contract_version"] == "1.0.0"


def test_unknown_parameter():
    assert_json_error(run_cli(*VALID_APRIORI, "--bilinmeyen", "1"), "UNKNOWN_PARAM", "bilinmeyen")


def test_missing_parameter():
    args = list(VALID_APRIORI)
    i = args.index("--alpha")
    del args[i:i + 2]
    assert_json_error(run_cli(*args), "MISSING_PARAM", "alpha")


@pytest.mark.parametrize("value", ["nan", "inf", "-inf"])
def test_nonfinite_values(value):
    args = list(VALID_APRIORI)
    i = args.index("--dz")
    args[i:i + 2] = [f"--dz={value}"]
    assert_json_error(run_cli(*args), "INVALID_VALUE", "dz")


def test_unsupported_family():
    args = list(VALID_APRIORI)
    args[args.index("--test") + 1] = "anova-oneway"
    assert_json_error(run_cli(*args), "UNSUPPORTED", "test")


def test_success_writes_nothing_to_stderr():
    proc = run_cli(*VALID_APRIORI)
    assert proc.returncode == 0
    assert proc.stderr == ""
    assert len(proc.stdout.strip().splitlines()) == 1


def _console_script(name):
    scripts = Path(sys.executable).parent
    for candidate in (scripts / f"{name}.exe", scripts / name):
        if candidate.exists():
            return candidate
    return None


@pytest.mark.parametrize("name", ["gpower-clone", "powerlab"])
def test_console_scripts_installed(name):
    script = _console_script(name)
    if script is None:
        pytest.skip(f"{name} konsol komutu kurulu değil (pip install -e . gerekli)")
    proc = subprocess.run([str(script), *VALID_APRIORI], capture_output=True, text=True, encoding="utf-8")
    assert proc.returncode == 0
    assert json.loads(proc.stdout)["n_total"] == 54
