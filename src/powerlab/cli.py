"""
src/powerlab/cli.py
İnce katman CLI arayüzü: argparse -> engine -> tek satır JSON.
Hesap mantığı içermez, yalnızca engine katmanını çağırır.

Çıktı sözleşmesi: başarı ve hata dahil her sonuç STDOUT'a tek satır JSON olarak yazılır;
hata durumunda {"error": "..."} ve sıfırdan farklı çıkış kodu (1: hesap/doğrulama, 2: argüman).
stderr'e hiçbir şey yazılmaz. --help normal metin yazar ve 0 ile çıkar.
Takma adlar ve tolerans kuralları: CONTRACT_ASSUMED.md (bölüm 2 ve 3).
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Optional

from powerlab.engine.solver import normalize_family, run_power_analysis

EXIT_ENGINE_ERROR = 1
EXIT_USAGE_ERROR = 2

MODES = ["a-priori", "a_priori", "apriori", "post-hoc", "post_hoc", "posthoc"]

# Aynı anlama gelen parametre adları (argparse dest adları).
N_ALIASES = ["n", "n_total"]
PREDICTOR_ALIASES = ["predictors", "u", "k"]

# Aile başına: etki büyüklüğü takma adları, motora giden anahtar, anlamsız (yasak) parametreler,
# --tails'in kullanılıp kullanılmadığı (CONTRACT_ASSUMED.md T1-T8).
FAMILY_RULES: Dict[str, Dict[str, Any]] = {
    "t-paired": {
        "effect_key": "dz",
        "effect_aliases": ["dz", "d", "effect"],
        "forbidden": ["f2", "predictors", "u", "k"],
        "uses_tails": True,
        "uses_predictors": False,
    },
    "multireg-r2": {
        "effect_key": "f2",
        "effect_aliases": ["f2", "effect"],
        "forbidden": ["dz", "d"],
        "uses_tails": False,  # F testi tek yönlü; --tails 1/2 yok sayılır
        "uses_predictors": True,
    },
}


def _emit(payload: dict) -> None:
    print(json.dumps(payload, separators=(",", ":")))


def _option(dest: str) -> str:
    return "--" + dest.replace("_", "-")


class JsonArgumentParser(argparse.ArgumentParser):
    """Argüman hatalarını (bilinmeyen/eksik parametre, geçersiz seçenek) JSON olarak bildirir."""

    def error(self, message: str) -> None:
        _emit({"error": f"Geçersiz argüman: {message}"})
        sys.exit(EXIT_USAGE_ERROR)


def build_parser() -> argparse.ArgumentParser:
    parser = JsonArgumentParser(
        prog="gpower-clone",
        allow_abbrev=False,  # "--pow" gibi kısaltmalar başka bir takma adla karışmasın
        description="powerlab: G*Power 3.1.9.7 davranışını referans alan bağımsız bir yeniden yazım; G*Power değildir.",
    )
    parser.add_argument("--test", type=str, required=True, help="Test ailesi: t-paired (multireg-r2 henüz uygulanmadı)")
    parser.add_argument("--mode", type=str, default="a-priori", choices=MODES, help="Analiz modu: a-priori veya post-hoc")
    parser.add_argument("--tails", type=int, default=None, choices=[1, 2],
                        help="Kuyruk sayısı (1 veya 2; varsayılan 2). multireg-r2'de yok sayılır")
    parser.add_argument("--dz", type=float, default=None, help="t-paired etki büyüklüğü dz")
    parser.add_argument("--d", type=float, default=None, help="--dz takma adı")
    parser.add_argument("--f2", type=float, default=None, help="multireg-r2 etki büyüklüğü f²")
    parser.add_argument("--effect", type=float, default=None, help="Aileye göre dz (t-paired) veya f² (multireg-r2)")
    parser.add_argument("--predictors", type=int, default=None, help="multireg-r2 yordayıcı sayısı")
    parser.add_argument("--u", type=int, default=None, help="--predictors takma adı")
    parser.add_argument("--k", type=int, default=None, help="--predictors takma adı")
    parser.add_argument("--alpha", type=float, required=True, help="Tip I hata oranı (alpha, örn: 0.05)")
    parser.add_argument("--power", type=float, default=None, help="Hedef güç (1 - beta, örn: 0.95)")
    parser.add_argument("--n", type=int, default=None, help="Post-hoc örneklem büyüklüğü (t-paired: çift sayısı)")
    parser.add_argument("--n-total", type=int, default=None, help="--n takma adı")
    parser.add_argument("--ratio", type=float, default=None, help="Grup oranı; bu ailelerde yalnızca 1 kabul edilir (yok sayılır)")
    return parser


def _resolve(parser: argparse.ArgumentParser, parsed: argparse.Namespace, dests: List[str]) -> Any:
    """Takma ad grubundan tek bir değer seçer; farklı değerler verilmişse argüman hatası."""
    given = [(d, getattr(parsed, d)) for d in dests if getattr(parsed, d) is not None]
    if len({repr(v) for _, v in given}) > 1:
        listed = ", ".join(f"{_option(d)}={v}" for d, v in given)
        parser.error(f"Çakışan parametreler: {listed}")
    return given[0][1] if given else None


def _build_params(parser: argparse.ArgumentParser, parsed: argparse.Namespace) -> Dict[str, Any]:
    family = normalize_family(parsed.test)
    params: Dict[str, Any] = {"alpha": parsed.alpha}
    if parsed.power is not None:
        params["power"] = parsed.power
    n_value = _resolve(parser, parsed, N_ALIASES)
    if n_value is not None:
        params["n"] = n_value

    rules = FAMILY_RULES.get(family)
    if rules is None:
        # Bilinmeyen aile: motor "desteklenmeyen test ailesi" hatası verir.
        params["tails"] = parsed.tails if parsed.tails is not None else 2
        return params

    for dest in rules["forbidden"]:
        if getattr(parsed, dest) is not None:
            parser.error(f"{_option(dest)} {family} için geçerli değil")
    if parsed.ratio is not None and parsed.ratio != 1:
        parser.error(f"--ratio={parsed.ratio} {family} için geçersiz (yalnızca 1 kabul edilir)")

    effect = _resolve(parser, parsed, rules["effect_aliases"])
    if effect is not None:
        params[rules["effect_key"]] = effect
    if rules["uses_tails"]:
        params["tails"] = parsed.tails if parsed.tails is not None else 2
    if rules["uses_predictors"]:
        predictors = _resolve(parser, parsed, PREDICTOR_ALIASES)
        if predictors is not None:
            params["predictors"] = predictors
    return params


def _force_utf8_streams() -> None:
    """Windows konsolunda Türkçe karakterler (--help metni vb.) bozulmasın."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError, OSError):
            pass


def main(args: Optional[List[str]] = None) -> None:
    _force_utf8_streams()
    parser = build_parser()
    parsed = parser.parse_args(args)
    params = _build_params(parser, parsed)

    try:
        result = run_power_analysis(test=parsed.test, mode=parsed.mode, params=params)
    except Exception as err:
        _emit({"error": str(err)})
        sys.exit(EXIT_ENGINE_ERROR)
    _emit(result)
    sys.exit(0)


if __name__ == "__main__":
    main()
