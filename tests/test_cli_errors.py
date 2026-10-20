"""
tests/test_cli_errors.py
CLI hata sözleşmesi: her hata STDOUT'a tek satır {"error": ...} yazar, çıkış kodu sıfırdan
farklıdır ve stderr boş kalır. --help normal çalışır.
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


def assert_json_error(proc, expected_code=None):
    assert proc.returncode != 0
    if expected_code is not None:
        assert proc.returncode == expected_code
    assert proc.stderr == "", f"stderr boş olmalı, alınan: {proc.stderr!r}"
    lines = proc.stdout.strip().splitlines()
    assert len(lines) == 1, f"tek satır JSON bekleniyordu: {proc.stdout!r}"
    payload = json.loads(lines[0])
    assert set(payload) == {"error"}
    return payload["error"]


def test_help_still_works():
    proc = run_cli("--help")
    assert proc.returncode == 0
    assert proc.stderr == ""
    assert proc.stdout.startswith("usage: gpower-clone")
    assert "Kuyruk sayısı" in proc.stdout  # UTF-8 Türkçe karakterler bozulmadan


def test_unknown_parameter():
    msg = assert_json_error(run_cli(*VALID_APRIORI, "--bilinmeyen", "1"), expected_code=2)
    assert "--bilinmeyen" in msg


@pytest.mark.parametrize("missing", ["--test", "--alpha"])
def test_missing_required_parameter(missing):
    args = list(VALID_APRIORI)
    i = args.index(missing)
    del args[i:i + 2]
    msg = assert_json_error(run_cli(*args), expected_code=2)
    assert missing in msg


@pytest.mark.parametrize(
    "flag, value",
    [("--tails", "3"), ("--mode", "bayesci")],
)
def test_invalid_choice(flag, value):
    args = list(VALID_APRIORI)
    args[args.index(flag) + 1] = value
    msg = assert_json_error(run_cli(*args), expected_code=2)
    assert flag in msg


@pytest.mark.parametrize("value", ["abc", "nan", "30.5"])
def test_invalid_type_for_n(value):
    msg = assert_json_error(
        run_cli("--test", "t-paired", "--mode", "post-hoc", "--dz", "0.5", "--alpha", "0.05", "--n", value),
        expected_code=2,
    )
    assert "--n" in msg


@pytest.mark.parametrize("value", ["nan", "inf", "-inf"])
@pytest.mark.parametrize("flag", ["--dz", "--alpha", "--power"])
def test_nonfinite_values(flag, value):
    # "--dz=-inf" biçimi: argparse "-inf"i ayrı yazıldığında bayrak sanar.
    args = list(VALID_APRIORI)
    i = args.index(flag)
    args[i:i + 2] = [f"{flag}={value}"]
    msg = assert_json_error(run_cli(*args), expected_code=1)
    assert "NaN/inf" in msg


def test_missing_effect_size():
    args = list(VALID_APRIORI)
    i = args.index("--dz")
    del args[i:i + 2]
    msg = assert_json_error(run_cli(*args), expected_code=1)
    assert "dz" in msg


def test_unsupported_family():
    args = list(VALID_APRIORI)
    args[args.index("--test") + 1] = "multireg-r2"
    assert_json_error(run_cli(*args), expected_code=1)


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
    assert json.loads(proc.stdout)["n"] == 54
