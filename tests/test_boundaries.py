"""
tests/test_boundaries.py
oracle/boundary_vectors.csv satırlarını okur.

- expected_behavior == "error": motor ValueError fırlatmalı; CLI stdout'a {"error": ...} yazıp
  sıfırdan farklı kodla çıkmalı.
- Diğer satırlar (B01-B05): beklenen değerler kâhinden gelmediği için boştur. Yalnızca SPEC
  kuralları denetlenir: çökme yok, n >= 2, actual_power >= hedef güç, df = n - 1.
  Bir beklenen sütun doluysa (G*Power ekran görüntüsüyle) o da karşılaştırılır.
"""

import csv
import json
from pathlib import Path

import pytest

from powerlab import cli
from powerlab.engine.solver import run_power_analysis

BOUNDARY_CSV = Path(__file__).parent.parent / "oracle" / "boundary_vectors.csv"


def load_rows():
    with open(BOUNDARY_CSV, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


ROWS = load_rows()
ERROR_ROWS = [r for r in ROWS if r["expected_behavior"] == "error"]
RULE_ROWS = [r for r in ROWS if r["expected_behavior"] != "error"]


def _engine_params(row):
    params = {"tails": int(row["tails"]), "dz": float(row["effect"]), "alpha": float(row["alpha"])}
    if row["mode"] == "a-priori":
        params["power"] = float(row["power"])
    else:
        params["n"] = int(row["n_input"])
    return params


def _cli_args(row):
    args = ["--test", row["family"], "--mode", row["mode"], f"--tails={row['tails']}",
            f"--dz={row['effect']}", f"--alpha={row['alpha']}"]
    if row["mode"] == "a-priori":
        args.append(f"--power={row['power']}")
    else:
        args.append(f"--n={row['n_input']}")
    return args


def test_csv_schema():
    assert ROWS, "boundary_vectors.csv boş"
    assert len(ROWS[0]) == 17
    assert {r["expected_behavior"] for r in ROWS} <= {"", "error"}


@pytest.mark.parametrize("row", ERROR_ROWS, ids=lambda r: r["id"])
def test_invalid_rows_raise_in_engine(row):
    with pytest.raises(ValueError):
        run_power_analysis(test=row["family"], mode=row["mode"], params=_engine_params(row))


@pytest.mark.parametrize("row", ERROR_ROWS, ids=lambda r: r["id"])
def test_invalid_rows_return_json_error_in_cli(capsys, row):
    with pytest.raises(SystemExit) as exc:
        cli.main(_cli_args(row))
    assert exc.value.code != 0
    out, err = capsys.readouterr()
    assert err == ""
    assert set(json.loads(out)) == {"error"}


@pytest.mark.parametrize("row", RULE_ROWS, ids=lambda r: r["id"])
def test_boundary_rows_satisfy_spec_rules(row):
    params = _engine_params(row)
    res = run_power_analysis(test=row["family"], mode=row["mode"], params=params)
    assert res["n"] >= 2
    assert res["df"] == res["n"] - 1
    if row["mode"] == "a-priori":
        assert res["actual_power"] >= params["power"]

    if row["n_expected"].strip():
        assert res["n"] == int(row["n_expected"])
