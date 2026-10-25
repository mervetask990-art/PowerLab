"""
tests/test_bonus_modes.py
t-paired bonus modları (CONTRACT.md §3, §4.2): compromise, criterion, sensitivity.

Kâhin: oracle/gpower_bonus_modes.csv (G*Power 3.1.9.7 ekran görüntüleri K01–K09; ondalıklar CSV'deki
basamak sayısına kadar, tam sayılar tam eşleşme). Eğitmen vektörleri test_public_vectors.py'de.
Hesap yalnızca motorda; CLI ve MCP aynı JSON'u verir.
"""

import csv
import json
from pathlib import Path

import pytest

from powerlab import cli
from powerlab.mcp_server import call_tool_text

ORACLE = Path(__file__).parent.parent / "oracle" / "gpower_bonus_modes.csv"
ROWS = list(csv.DictReader(open(ORACLE, encoding="utf-8")))

# Mod -> (girdi alanları, CSV sütunu), (çıktı alanı, beklenen sütun). Sıra CONTRACT.md §4.2.
INPUTS = {
    "compromise": [("tails", "tails"), ("dz", "effect"), ("beta_alpha_ratio", "beta_alpha_ratio"), ("n_total", "n_input")],
    "criterion": [("tails", "tails"), ("dz", "effect"), ("power", "power"), ("n_total", "n_input")],
    "sensitivity": [("tails", "tails"), ("alpha", "alpha"), ("power", "power"), ("n_total", "n_input")],
}
OUTPUTS = {
    "compromise": [("ncp", "ncp_expected"), ("critical_t", "critical_expected"), ("df", "df_expected"),
                   ("alpha", "alpha_expected"), ("beta", "beta_expected"), ("power", "power_expected")],
    "criterion": [("ncp", "ncp_expected"), ("critical_t", "critical_expected"), ("df", "df_expected"),
                  ("alpha", "alpha_expected")],
    "sensitivity": [("ncp", "ncp_expected"), ("critical_t", "critical_expected"), ("df", "df_expected"),
                    ("dz", "effect_expected")],
}


def request(row):
    return {"test": "t-paired", "mode": row["mode"], **{f: row[c] for f, c in INPUTS[row["mode"]]}}


def to_args(fields):
    args = []
    for key, value in fields.items():
        args += [f"--{key}", str(value)]
    return args


def run(capsys, args):
    with pytest.raises(SystemExit) as exc:
        cli.main(args)
    out, err = capsys.readouterr()
    assert err == ""
    lines = out.strip().splitlines()
    assert len(lines) == 1
    return exc.value.code, lines[0]


def decimals(text):
    return len(text.split(".", 1)[1]) if "." in text else 0


def test_oracle_has_nine_vectors():
    assert [r["id"] for r in ROWS] == [f"K0{i}" for i in range(1, 10)]


@pytest.mark.parametrize("row", ROWS, ids=lambda r: r["id"])
def test_gpower_bonus_vector(capsys, row):
    code, line = run(capsys, to_args(request(row)))
    assert code == 0, line
    data = json.loads(line)
    assert list(data) == [name for name, _ in OUTPUTS[row["mode"]]]
    for name, column in OUTPUTS[row["mode"]]:
        text = row[column]
        if name == "df":
            assert type(data[name]) is int and data[name] == int(text)
        else:
            places = decimals(text)
            assert abs(data[name] - float(text)) <= 0.5 * 10 ** -places + 1e-12, (
                f"{row['id']} {name}: beklenen={text}, hesaplanan={data[name]}"
            )


@pytest.mark.parametrize("row", ROWS, ids=lambda r: r["id"])
def test_cli_equals_mcp(capsys, row):
    _, line = run(capsys, to_args(request(row)))
    assert call_tool_text("power_analysis", request(row)) == line


def test_compromise_beta_is_ratio_times_alpha(capsys):
    row = next(r for r in ROWS if r["id"] == "K02")
    _, line = run(capsys, to_args(request(row)))
    data = json.loads(line)
    assert abs(data["beta"] - 4 * data["alpha"]) < 1e-9
    assert abs(data["power"] - (1 - data["beta"])) < 1e-12


COMPROMISE = ["--test", "t-paired", "--mode", "compromise", "--tails", "2", "--dz", "0.5",
              "--beta_alpha_ratio", "1", "--n_total", "54"]
CRITERION = ["--test", "t-paired", "--mode", "criterion", "--tails", "2", "--dz", "0.5",
             "--power", "0.95", "--n_total", "54"]
SENSITIVITY = ["--test", "t-paired", "--mode", "sensitivity", "--tails", "2", "--alpha", "0.05",
               "--power", "0.95", "--n_total", "54"]


def replaced(args, flag, value):
    out = list(args)
    out[out.index(flag) + 1] = value
    return out


def without(args, flag):
    out = list(args)
    i = out.index(flag)
    del out[i:i + 2]
    return out


@pytest.mark.parametrize(
    "args, code, field",
    [
        (without(COMPROMISE, "--beta_alpha_ratio"), "MISSING_PARAM", "beta_alpha_ratio"),
        (COMPROMISE + ["--power", "0.8"], "UNKNOWN_PARAM", "power"),
        (COMPROMISE + ["--alpha", "0.05"], "UNKNOWN_PARAM", "alpha"),
        (replaced(COMPROMISE, "--beta_alpha_ratio", "0"), "OUT_OF_RANGE", "beta_alpha_ratio"),
        (replaced(COMPROMISE, "--beta_alpha_ratio", "-1"), "OUT_OF_RANGE", "beta_alpha_ratio"),
        (replaced(COMPROMISE, "--n_total", "2"), "OUT_OF_RANGE", "n_total"),
        (replaced(COMPROMISE, "--dz", "0"), "OUT_OF_RANGE", "dz"),
        (CRITERION + ["--alpha", "0.05"], "UNKNOWN_PARAM", "alpha"),
        (replaced(CRITERION, "--n_total", "2"), "OUT_OF_RANGE", "n_total"),
        (replaced(CRITERION, "--power", "1"), "OUT_OF_RANGE", "power"),
        (SENSITIVITY + ["--dz", "0.5"], "UNKNOWN_PARAM", "dz"),
        (replaced(SENSITIVITY, "--power", "0.03"), "INCONSISTENT", "power"),
        (replaced(SENSITIVITY, "--n_total", "2"), "OUT_OF_RANGE", "n_total"),
        (without(SENSITIVITY, "--tails"), "MISSING_PARAM", "tails"),
    ],
    ids=["oran-eksik", "comp-power", "comp-alpha", "oran-0", "oran-negatif", "comp-n2", "comp-dz0",
         "crit-alpha", "crit-n2", "crit-power1", "sens-dz", "sens-guc-alfadan-kucuk", "sens-n2", "sens-tails-eksik"],
)
def test_bonus_mode_errors(capsys, args, code, field):
    exit_code, line = run(capsys, args)
    data = json.loads(line)
    assert exit_code == 2
    assert (data["code"], data["field"]) == (code, field)
