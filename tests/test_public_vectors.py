"""
tests/test_public_vectors.py
Eğitmen protokolü kâhini: oracle/public_vectors.jsonl (CONTRACT.md §9, satır satır aynen).
Karşılaştırma CONTRACT.md §6: tam sayılar tam eşleşme; ondalıklar |fark| <= 1e-6 ya da göreli <= 1e-6.
Uygulanmayan aile/modlar UNSUPPORTED (çıkış kodu 2) döner.
"""

import json
from pathlib import Path

import pytest

from powerlab import cli

PUBLIC = Path(__file__).parent.parent / "oracle" / "public_vectors.jsonl"
VECTORS = [json.loads(line) for line in PUBLIC.read_text(encoding="utf-8").splitlines() if line.strip()]
IMPLEMENTED = {(test, mode) for test in ("t-paired", "multireg-r2")
               for mode in ("a-priori", "post-hoc", "compromise", "criterion", "sensitivity")}


def is_implemented(vec):
    return (vec["input"]["test"], vec["input"]["mode"]) in IMPLEMENTED


def to_args(inp):
    args = []
    for key, value in inp.items():
        args += [f"--{key}", str(value)]
    return args


def run(capsys, args):
    with pytest.raises(SystemExit) as exc:
        cli.main(args)
    out, err = capsys.readouterr()
    assert err == ""
    return exc.value.code, json.loads(out)


def test_file_has_25_vectors():
    assert len(VECTORS) == 25
    assert len({v["id"] for v in VECTORS}) == 25


@pytest.mark.parametrize("vec", [v for v in VECTORS if is_implemented(v)], ids=lambda v: v["id"])
def test_implemented_public_vector(capsys, vec):
    code, data = run(capsys, to_args(vec["input"]))
    assert code == 0, data
    for key, expected in vec["expected"].items():
        got = data[key]
        if isinstance(expected, int):
            assert type(got) is int and got == expected, key
        else:
            diff = abs(got - expected)
            assert diff <= 1e-6 or diff <= 1e-6 * abs(expected), f"{key}: beklenen={expected}, hesaplanan={got}"


@pytest.mark.parametrize("vec", [v for v in VECTORS if not is_implemented(v)], ids=lambda v: v["id"])
def test_unimplemented_public_vector_is_unsupported(capsys, vec):
    code, data = run(capsys, to_args(vec["input"]))
    assert code == 2
    assert data["code"] == "UNSUPPORTED"
