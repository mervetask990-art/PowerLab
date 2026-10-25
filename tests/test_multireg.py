"""
tests/test_multireg.py
multireg-r2 (bonus aile, CONTRACT.md §4.5): Linear multiple regression, Fixed model, R² deviation from zero.

Kâhin: oracle/gpower_multireg.csv (G*Power 3.1.9.7 ekran görüntüleri M01–M28; ondalıklar CSV'deki basamak
sayısına kadar, tam sayılar tam eşleşme). Eğitmen vektörleri (5 mod) test_public_vectors.py'de.
G*Power'ın hata verdiği satırlarda motor sözleşme kodlu hata döner. M25 (post hoc f² = 0) CONTRACT.md §5
(f2 > 0) gereği kasıtlı sapmadır: G*Power güç = α verir, motor OUT_OF_RANGE döner.
"""

import csv
import json
from pathlib import Path

import pytest

from powerlab import cli
from powerlab.mcp_server import call_tool_text

ORACLE = Path(__file__).parent.parent / "oracle" / "gpower_multireg.csv"
ROWS = list(csv.DictReader(open(ORACLE, encoding="utf-8")))

OUTPUTS = {
    "a-priori": [("ncp", "ncp_expected"), ("critical_f", "critical_expected"), ("df1", "df1_expected"),
                 ("df2", "df2_expected"), ("n_total", "n_expected"), ("actual_power", "power_expected")],
    "post-hoc": [("ncp", "ncp_expected"), ("critical_f", "critical_expected"), ("df1", "df1_expected"),
                 ("df2", "df2_expected"), ("power", "power_expected")],
}
INTEGER_OUTPUTS = {"df1", "df2", "n_total"}

# G*Power'ın hata verdiği vektörler -> beklenen sözleşme kodu ve alanı.
GPOWER_ERRORS = {
    "M14": ("INCONSISTENT", "power"),
    "M15": ("OUT_OF_RANGE", "f2"),
    "M16": ("OUT_OF_RANGE", "predictors"),
    "M26": ("OUT_OF_RANGE", "n_total"),
    "M28": ("OUT_OF_RANGE", "f2"),
}
# CONTRACT.md §5 gereği kasıtlı sapma: G*Power hesaplar, sözleşme f2 > 0 ister.
CONTRACT_DEVIATIONS = {"M25": ("OUT_OF_RANGE", "f2")}

NUMERIC = [r for r in ROWS if r["id"] not in GPOWER_ERRORS and r["id"] not in CONTRACT_DEVIATIONS]


def request(row):
    fields = {"test": "multireg-r2", "mode": row["mode"], "f2": row["effect"], "alpha": row["alpha"],
              "predictors": row["predictors"]}
    if row["mode"] == "a-priori":
        fields["power"] = row["power"]
    else:
        fields["n_total"] = row["n_input"]
    return fields


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


def test_oracle_has_28_vectors_23_numeric():
    assert [r["id"] for r in ROWS] == [f"M{i:02d}" for i in range(1, 29)]
    assert len(NUMERIC) == 22  # 23 sayısal kâhinden M25 kasıtlı sapma olarak ayrıldı
    assert all(r["gpower_error"] for r in ROWS if r["id"] in GPOWER_ERRORS)


@pytest.mark.parametrize("row", NUMERIC, ids=lambda r: r["id"])
def test_gpower_multireg_vector(capsys, row):
    code, line = run(capsys, to_args(request(row)))
    assert code == 0, line
    data = json.loads(line)
    assert list(data) == [name for name, _ in OUTPUTS[row["mode"]]]
    for name, column in OUTPUTS[row["mode"]]:
        text = row[column]
        if name in INTEGER_OUTPUTS:
            assert type(data[name]) is int and data[name] == int(text), f"{row['id']} {name}"
        else:
            places = decimals(text)
            assert abs(data[name] - float(text)) <= 0.5 * 10 ** -places + 1e-12, (
                f"{row['id']} {name}: beklenen={text}, hesaplanan={data[name]}"
            )


@pytest.mark.parametrize("vid", sorted(GPOWER_ERRORS), ids=str)
def test_gpower_error_vectors(capsys, vid):
    row = next(r for r in ROWS if r["id"] == vid)
    code, line = run(capsys, to_args(request(row)))
    data = json.loads(line)
    assert code == 2
    assert (data["code"], data["field"]) == GPOWER_ERRORS[vid]


@pytest.mark.parametrize("vid", sorted(CONTRACT_DEVIATIONS), ids=str)
def test_contract_deviation_vectors(capsys, vid):
    row = next(r for r in ROWS if r["id"] == vid)
    code, line = run(capsys, to_args(request(row)))
    data = json.loads(line)
    assert code == 2
    assert (data["code"], data["field"]) == CONTRACT_DEVIATIONS[vid]


@pytest.mark.parametrize("row", NUMERIC, ids=lambda r: r["id"])
def test_cli_equals_mcp(capsys, row):
    _, line = run(capsys, to_args(request(row)))
    assert call_tool_text("power_analysis", request(row)) == line


APRIORI = ["--test", "multireg-r2", "--mode", "a-priori", "--f2", "0.15", "--alpha", "0.05",
           "--power", "0.80", "--predictors", "5"]
POSTHOC = ["--test", "multireg-r2", "--mode", "post-hoc", "--f2", "0.15", "--alpha", "0.05",
           "--n_total", "100", "--predictors", "5"]


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
        (APRIORI + ["--tails", "2"], "UNKNOWN_PARAM", "tails"),
        (APRIORI + ["--dz", "0.5"], "UNKNOWN_PARAM", "dz"),
        (without(APRIORI, "--predictors"), "MISSING_PARAM", "predictors"),
        (replaced(APRIORI, "--predictors", "2.5"), "INVALID_VALUE", "predictors"),
        (replaced(APRIORI, "--f2", "50.5"), "OUT_OF_RANGE", "f2"),
        (replaced(APRIORI, "--f2", "-0.1"), "OUT_OF_RANGE", "f2"),
        (replaced(POSTHOC, "--n_total", "6"), "OUT_OF_RANGE", "n_total"),
        (replaced(POSTHOC, "--predictors", "0"), "OUT_OF_RANGE", "predictors"),
        (POSTHOC + ["--power", "0.8"], "UNKNOWN_PARAM", "power"),
    ],
    ids=["tails-ilgisiz", "dz-ilgisiz", "predictors-eksik", "predictors-ondalik", "f2-50-ustu",
         "f2-negatif", "posthoc-n-yetersiz", "posthoc-predictors-0", "posthoc-power-ilgisiz"],
)
def test_multireg_errors(capsys, args, code, field):
    exit_code, line = run(capsys, args)
    data = json.loads(line)
    assert exit_code == 2
    assert (data["code"], data["field"]) == (code, field)


def test_posthoc_minimum_n_is_predictors_plus_two(capsys):
    """M27: N = yordayıcı + 2 kabul edilir (df2 = 1), M26: N = yordayıcı + 1 reddedilir."""
    code, line = run(capsys, replaced(POSTHOC, "--n_total", "7"))
    assert code == 0
    assert json.loads(line)["df2"] == 1
