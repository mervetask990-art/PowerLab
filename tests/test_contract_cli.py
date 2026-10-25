"""
tests/test_contract_cli.py
CONTRACT.md 1.0.0 arayüzü (t-paired), CLI süreç içinde çağrılarak:
- Çıktı alanları birebir ve sıralı (§4.2); tam sayılar JSON int; ondalıklar tam double (§2.3).
- Varsayılan yok, takma ad yok (§2.1); hata {"error","code","field"} ve çıkış kodu 2 (§2.4).
- --version (§2.2), --help çıkış kodu 0.

Hata önceliği: test/mode eksik -> test/mode desteklenmiyor -> tanınmayan alan -> eksik alan
-> değer biçimi -> aralık (§5 ve G*Power'ın aralık içindeki retleri) -> tutarlılık.
"""

import json
import math

import pytest

from powerlab import cli

APRIORI = ["--test", "t-paired", "--mode", "a-priori", "--tails", "1",
           "--dz", "0.5", "--alpha", "0.05", "--power", "0.95"]
POSTHOC = ["--test", "t-paired", "--mode", "post-hoc", "--tails", "1",
           "--dz", "0.5", "--alpha", "0.05", "--n_total", "45"]


def run(capsys, *args):
    with pytest.raises(SystemExit) as exc:
        cli.main(list(args))
    out, err = capsys.readouterr()
    assert err == "", f"stderr boş olmalı: {err!r}"
    lines = out.strip().splitlines()
    assert len(lines) == 1, f"tek satır JSON bekleniyordu: {out!r}"
    return exc.value.code, json.loads(lines[0])


def without(args, flag):
    i = args.index(flag)
    return args[:i] + args[i + 2:]


def replaced(args, flag, value):
    i = args.index(flag)
    return args[:i] + [f"{flag}={value}"] + args[i + 2:]


def test_apriori_fields_order_and_types(capsys):
    code, data = run(capsys, *APRIORI)
    assert code == 0
    assert list(data) == ["ncp", "critical_t", "df", "n_total", "actual_power"]
    assert type(data["df"]) is int and type(data["n_total"]) is int
    assert (data["df"], data["n_total"]) == (44, 45)


def test_posthoc_fields_order_and_types(capsys):
    code, data = run(capsys, *POSTHOC)
    assert code == 0
    assert list(data) == ["ncp", "critical_t", "df", "power"]
    assert type(data["df"]) is int and data["df"] == 44


def test_output_is_full_double(capsys):
    _, data = run(capsys, *POSTHOC)
    assert data["ncp"] == 0.5 * math.sqrt(45)  # 7 ondalığa yuvarlanmış değil


def test_version(capsys):
    code, data = run(capsys, "--version")
    assert code == 0
    assert data["contract_version"] == "1.0.0"
    assert {"contract_version", "name", "engine"} <= set(data)


def test_help_exit_code_zero(capsys):
    with pytest.raises(SystemExit) as exc:
        cli.main(["--help"])
    out, err = capsys.readouterr()
    assert exc.value.code == 0
    assert err == ""
    assert out.startswith("usage: gpower-clone")


ERRORS = [
    ("eksik-tails", without(APRIORI, "--tails"), "MISSING_PARAM", "tails"),
    ("eksik-dz", without(APRIORI, "--dz"), "MISSING_PARAM", "dz"),
    ("eksik-alpha", without(APRIORI, "--alpha"), "MISSING_PARAM", "alpha"),
    ("eksik-power", without(APRIORI, "--power"), "MISSING_PARAM", "power"),
    ("eksik-n_total", without(POSTHOC, "--n_total"), "MISSING_PARAM", "n_total"),
    ("eksik-test", without(APRIORI, "--test"), "MISSING_PARAM", "test"),
    ("eksik-mode", without(APRIORI, "--mode"), "MISSING_PARAM", "mode"),
    ("eski-takma-ad-n", without(POSTHOC, "--n_total") + ["--n", "45"], "UNKNOWN_PARAM", "n"),
    ("eski-takma-ad-n-total", without(POSTHOC, "--n_total") + ["--n-total", "45"], "UNKNOWN_PARAM", "n-total"),
    ("eski-takma-ad-d", without(APRIORI, "--dz") + ["--d", "0.5"], "UNKNOWN_PARAM", "d"),
    ("eski-takma-ad-effect", without(APRIORI, "--dz") + ["--effect", "0.5"], "UNKNOWN_PARAM", "effect"),
    ("ratio-1", APRIORI + ["--ratio", "1"], "UNKNOWN_PARAM", "ratio"),
    ("post-hoc-ta-power", POSTHOC + ["--power", "0.8"], "UNKNOWN_PARAM", "power"),
    ("a-priori-de-n_total", APRIORI + ["--n_total", "45"], "UNKNOWN_PARAM", "n_total"),
    ("bilinmeyen-alan", APRIORI + ["--bilinmeyen", "1"], "UNKNOWN_PARAM", "bilinmeyen"),
    ("fazla-konumsal", APRIORI + ["fazla"], "UNKNOWN_PARAM", "fazla"),
    ("mod-takma-adi", replaced(APRIORI, "--mode", "a_priori"), "UNSUPPORTED", "mode"),
    ("bilinmeyen-mod", replaced(APRIORI, "--mode", "bayesci"), "UNSUPPORTED", "mode"),
    ("bonus-mod-ilgisiz-alan", replaced(APRIORI, "--mode", "compromise"), "UNKNOWN_PARAM", "alpha"),
    ("kapsam-disi-aile", replaced(APRIORI, "--test", "chi2-contingency"), "UNSUPPORTED", "test"),
    ("diger-aile", replaced(APRIORI, "--test", "t2-indep"), "UNSUPPORTED", "test"),
    ("bilinmeyen-aile", replaced(APRIORI, "--test", "bayes"), "UNSUPPORTED", "test"),
    ("tails-3", replaced(APRIORI, "--tails", "3"), "OUT_OF_RANGE", "tails"),
    ("tails-ondalik", replaced(APRIORI, "--tails", "1.5"), "INVALID_VALUE", "tails"),
    ("n_total-ondalik", replaced(POSTHOC, "--n_total", "30.5"), "INVALID_VALUE", "n_total"),
    ("n_total-metin", replaced(POSTHOC, "--n_total", "abc"), "INVALID_VALUE", "n_total"),
    ("alpha-metin", replaced(APRIORI, "--alpha", "abc"), "INVALID_VALUE", "alpha"),
    ("dz-nan", replaced(APRIORI, "--dz", "nan"), "INVALID_VALUE", "dz"),
    ("alpha-inf", replaced(APRIORI, "--alpha", "inf"), "INVALID_VALUE", "alpha"),
    ("deger-yok", APRIORI[:-1], "INVALID_VALUE", "power"),
    ("tekrarlanan-alan", APRIORI + ["--alpha", "0.05"], "INVALID_VALUE", "alpha"),
    ("alpha-0", replaced(APRIORI, "--alpha", "0"), "OUT_OF_RANGE", "alpha"),
    ("alpha-1", replaced(APRIORI, "--alpha", "1"), "OUT_OF_RANGE", "alpha"),
    ("power-1", replaced(APRIORI, "--power", "1"), "OUT_OF_RANGE", "power"),
    # CONTRACT.md §5: dz > 0. G*Power negatif dz ve post hoc dz=0 ile hesap yapar (LEDGER L13, L16).
    ("dz-0-a-priori", replaced(APRIORI, "--dz", "0"), "OUT_OF_RANGE", "dz"),
    ("dz-negatif-a-priori", replaced(APRIORI, "--dz", "-0.5"), "OUT_OF_RANGE", "dz"),
    ("dz-0-post-hoc", replaced(POSTHOC, "--dz", "0"), "OUT_OF_RANGE", "dz"),
    ("dz-negatif-post-hoc", replaced(POSTHOC, "--dz", "-0.5"), "OUT_OF_RANGE", "dz"),
    # G*Power'ın §5 aralığı içinde reddettikleri (LEDGER L18, L19, L20).
    ("dz-esik-alti-a-priori", replaced(APRIORI, "--dz", "0.000005"), "OUT_OF_RANGE", "dz"),
    ("n_total-1", replaced(POSTHOC, "--n_total", "1"), "OUT_OF_RANGE", "n_total"),
    ("n_total-2-post-hoc", replaced(POSTHOC, "--n_total", "2"), "OUT_OF_RANGE", "n_total"),
    ("power-alfadan-kucuk", replaced(APRIORI, "--power", "0.03"), "INCONSISTENT", "power"),
    # α ve güç [1e-7, 0.9999999] kapalı aralığında ([REA] 0x487530 / 0x488110, LEDGER L32).
    ("alpha-1e-8", replaced(APRIORI, "--alpha", "1e-8"), "OUT_OF_RANGE", "alpha"),
    ("alpha-0.99999995-post-hoc", replaced(POSTHOC, "--alpha", "0.99999995"), "OUT_OF_RANGE", "alpha"),
    ("power-0.99999999", replaced(APRIORI, "--power", "0.99999999"), "OUT_OF_RANGE", "power"),
    # Post hoc'ta dz <= 20 ([REA] 0x487b70, LEDGER L33).
    ("dz-20.5-post-hoc", replaced(POSTHOC, "--dz", "20.5"), "OUT_OF_RANGE", "dz"),
    # A priori kontrol sırası: dz eşiği α'dan önce ([REA] L32).
    ("sira-dz-esigi-alfadan-once", replaced(replaced(APRIORI, "--dz", "0.000005"), "--alpha", "0"), "OUT_OF_RANGE", "dz"),
]


@pytest.mark.parametrize("args, code, field", [e[1:] for e in ERRORS], ids=[e[0] for e in ERRORS])
def test_invalid_input(capsys, args, code, field):
    exit_code, data = run(capsys, *args)
    assert exit_code == 2
    assert list(data) == ["error", "code", "field"]
    assert data["error"]
    assert (data["code"], data["field"]) == (code, field)


ACCEPTED = [
    # [REA] L32 aralığının uçları kapalıdır.
    ("alpha-1e-7", replaced(APRIORI, "--alpha", "1e-7")),
    ("power-0.9999999", replaced(APRIORI, "--power", "0.9999999")),
    # [REA] L33: post hoc'ta dz = 20 kabul; a priori'de dz için üst sınır yok.
    ("dz-20-post-hoc", replaced(POSTHOC, "--dz", "20")),
    ("dz-25-a-priori", replaced(APRIORI, "--dz", "25")),
]


@pytest.mark.parametrize("args", [a[1] for a in ACCEPTED], ids=[a[0] for a in ACCEPTED])
def test_gpower_range_edges_are_accepted(capsys, args):
    code, data = run(capsys, *args)
    assert code == 0, data


def test_power_equal_alpha_is_accepted(capsys):
    code, data = run(capsys, *replaced(APRIORI, "--power", "0.05"))
    assert code == 0
    assert data["n_total"] == 2
