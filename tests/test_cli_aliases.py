"""
tests/test_cli_aliases.py
CLI takma adları, çakışma kontrolü ve aileye ait olmayan parametre toleransı
(CONTRACT_ASSUMED.md bölüm 2 ve 3). CLI süreç içinde çağrılır.
"""

import json

import pytest

from powerlab import cli

BASE_APRIORI = ["--test", "t-paired", "--mode", "a-priori", "--tails", "2", "--alpha", "0.05", "--power", "0.95"]
BASE_POSTHOC = ["--test", "t-paired", "--mode", "post-hoc", "--tails", "2", "--dz", "0.5", "--alpha", "0.05"]
MULTIREG = ["--test", "multireg-r2", "--mode", "a-priori", "--alpha", "0.05", "--power", "0.8"]
NOT_IMPLEMENTED = "multireg-r2 henüz uygulanmadı"


def run(capsys, *args):
    with pytest.raises(SystemExit) as exc:
        cli.main(list(args))
    out, err = capsys.readouterr()
    assert err == "", f"stderr boş olmalı: {err!r}"
    lines = out.strip().splitlines()
    assert len(lines) == 1, f"tek satır JSON bekleniyordu: {out!r}"
    return exc.value.code, json.loads(lines[0])


@pytest.fixture
def reference(capsys):
    code, data = run(capsys, *BASE_APRIORI, "--dz", "0.5")
    assert code == 0
    return data


@pytest.fixture
def reference_posthoc(capsys):
    code, data = run(capsys, *BASE_POSTHOC, "--n", "54")
    assert code == 0
    return data


# --- t-paired etki büyüklüğü takma adları ---

@pytest.mark.parametrize("flag", ["--dz", "--d", "--effect"])
def test_tpaired_effect_aliases(capsys, reference, flag):
    code, data = run(capsys, *BASE_APRIORI, flag, "0.5")
    assert code == 0
    assert data == reference


# --- post-hoc örneklem takma adları ---

@pytest.mark.parametrize("flag", ["--n", "--n-total"])
def test_posthoc_n_aliases(capsys, reference_posthoc, flag):
    code, data = run(capsys, *BASE_POSTHOC, flag, "54")
    assert code == 0
    assert data == reference_posthoc


# --- mod adları ---

@pytest.mark.parametrize("mode", ["a-priori", "a_priori", "apriori"])
def test_apriori_mode_aliases(capsys, reference, mode):
    args = list(BASE_APRIORI)
    args[args.index("--mode") + 1] = mode
    code, data = run(capsys, *args, "--dz", "0.5")
    assert code == 0
    assert data == reference


@pytest.mark.parametrize("mode", ["post-hoc", "post_hoc", "posthoc"])
def test_posthoc_mode_aliases(capsys, reference_posthoc, mode):
    args = list(BASE_POSTHOC)
    args[args.index("--mode") + 1] = mode
    code, data = run(capsys, *args, "--n", "54")
    assert code == 0
    assert data == reference_posthoc


# --- çakışma kontrolü ---

@pytest.mark.parametrize(
    "extra",
    [
        ["--dz", "0.5", "--d", "0.6"],
        ["--dz", "0.5", "--effect", "0.6"],
        ["--d", "0.5", "--effect", "0.6"],
    ],
)
def test_conflicting_effect_aliases(capsys, extra):
    code, data = run(capsys, *BASE_APRIORI, *extra)
    assert code == 2
    assert "Çakışan parametreler" in data["error"]


def test_conflicting_n_aliases(capsys):
    code, data = run(capsys, *BASE_POSTHOC, "--n", "54", "--n-total", "30")
    assert code == 2
    assert "Çakışan parametreler" in data["error"]


def test_same_value_under_two_aliases_is_ok(capsys, reference):
    code, data = run(capsys, *BASE_APRIORI, "--dz", "0.5", "--d", "0.50", "--effect", "0.5")
    assert code == 0
    assert data == reference


def test_abbreviations_are_rejected(capsys):
    code, data = run(capsys, *BASE_APRIORI, "--dz", "0.5", "--rat", "1")
    assert code == 2


# --- t-paired tolerans kuralları (T1-T3) ---

def test_tpaired_ratio_one_is_ignored(capsys, reference):
    code, data = run(capsys, *BASE_APRIORI, "--dz", "0.5", "--ratio", "1")
    assert code == 0
    assert data == reference


@pytest.mark.parametrize("value", ["2", "0.5", "nan"])
def test_tpaired_ratio_other_than_one_is_error(capsys, value):
    code, data = run(capsys, *BASE_APRIORI, "--dz", "0.5", f"--ratio={value}")
    assert code == 2
    assert "--ratio" in data["error"]


@pytest.mark.parametrize(
    "flag, value",
    [("--f2", "0.15"), ("--predictors", "5"), ("--u", "5"), ("--k", "5")],
)
def test_tpaired_rejects_regression_params(capsys, flag, value):
    code, data = run(capsys, *BASE_APRIORI, "--dz", "0.5", flag, value)
    assert code == 2
    assert flag in data["error"]


# --- multireg-r2: takma adlar tanınır, motor henüz yok ---

@pytest.mark.parametrize("effect_flag", ["--f2", "--effect"])
@pytest.mark.parametrize("pred_flag", ["--predictors", "--u", "--k"])
def test_multireg_aliases_recognized(capsys, effect_flag, pred_flag):
    code, data = run(capsys, *MULTIREG, effect_flag, "0.15", pred_flag, "5")
    assert code == 1
    assert data == {"error": NOT_IMPLEMENTED}


def test_multireg_posthoc_n_total_recognized(capsys):
    args = ["--test", "multireg-r2", "--mode", "post-hoc", "--alpha", "0.05",
            "--f2", "0.15", "--predictors", "5", "--n-total", "100"]
    code, data = run(capsys, *args)
    assert code == 1
    assert data == {"error": NOT_IMPLEMENTED}


def test_multireg_conflicting_effect_aliases(capsys):
    code, data = run(capsys, *MULTIREG, "--f2", "0.15", "--effect", "0.35", "--predictors", "5")
    assert code == 2
    assert "Çakışan parametreler" in data["error"]


def test_multireg_conflicting_predictor_aliases(capsys):
    code, data = run(capsys, *MULTIREG, "--f2", "0.15", "--predictors", "5", "--k", "3")
    assert code == 2
    assert "Çakışan parametreler" in data["error"]


# --- multireg-r2 tolerans kuralları (T4-T8) ---

@pytest.mark.parametrize("tails", ["1", "2"])
def test_multireg_tails_is_ignored(capsys, tails):
    code, data = run(capsys, *MULTIREG, "--f2", "0.15", "--predictors", "5", "--tails", tails)
    assert code == 1
    assert data == {"error": NOT_IMPLEMENTED}


def test_multireg_invalid_tails_is_error(capsys):
    code, data = run(capsys, *MULTIREG, "--f2", "0.15", "--predictors", "5", "--tails", "3")
    assert code == 2
    assert "--tails" in data["error"]


def test_multireg_ratio_one_is_ignored(capsys):
    code, data = run(capsys, *MULTIREG, "--f2", "0.15", "--predictors", "5", "--ratio", "1")
    assert code == 1
    assert data == {"error": NOT_IMPLEMENTED}


def test_multireg_ratio_other_than_one_is_error(capsys):
    code, data = run(capsys, *MULTIREG, "--f2", "0.15", "--predictors", "5", "--ratio", "2")
    assert code == 2
    assert "--ratio" in data["error"]


@pytest.mark.parametrize("flag", ["--dz", "--d"])
def test_multireg_rejects_t_effect_sizes(capsys, flag):
    code, data = run(capsys, *MULTIREG, "--f2", "0.15", "--predictors", "5", flag, "0.5")
    assert code == 2
    assert flag in data["error"]
