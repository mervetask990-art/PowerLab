"""
src/powerlab/engine/contract.py
CONTRACT.md 1.0.0 istek katmanı: alan sözlüğü -> doğrulama -> motor -> sözleşme çıktısı.
CLI ve MCP yalnızca bu modülü çağırır; aynı istek iki arayüzde de aynı JSON metnini verir (§7).
Hesap yapmaz; hesap families/ altındadır.

Hata önceliği: test/mode eksik -> test/mode desteklenmiyor -> tanınmayan ya da modla ilgisiz alan
-> eksik alan -> değer biçimi -> aralık ve tutarlılık (motor).
"""

import json
import math
import platform
import re
from typing import Any, Dict, Tuple

from powerlab.engine.errors import INVALID_VALUE, MISSING_PARAM, UNKNOWN_PARAM, ContractError
from powerlab.engine.solver import check_supported, run_power_analysis

CONTRACT_VERSION = "1.0.0"
# --version çıktısındaki takım adı (CONTRACT.md §2.2).
TEAM_NAME = "<TAKIM_ADI>"

EXIT_OK = 0
EXIT_INTERNAL_ERROR = 1
EXIT_INVALID_INPUT = 2

# (test, mod) -> (girdi alanları, çıktı alanları); sıra CONTRACT.md §4.2 tablosundaki gibidir.
FIELDS = {
    ("t-paired", "a-priori"): (("tails", "dz", "alpha", "power"),
                               ("ncp", "critical_t", "df", "n_total", "actual_power")),
    ("t-paired", "post-hoc"): (("tails", "dz", "alpha", "n_total"),
                               ("ncp", "critical_t", "df", "power")),
}
INTEGER_FIELDS = {"tails", "n_total", "n1", "n2", "groups", "df", "predictors"}

# Sözleşme alanı -> motorun iç parametre adı.
ENGINE_PARAM = {"n_total": "n"}
# Sözleşme çıktı alanı -> motorun iç sonuç anahtarı.
OUTPUT_SOURCE = {"ncp": "ncp", "critical_t": "critical", "df": "df", "n_total": "n",
                 "actual_power": "actual_power", "power": "actual_power"}

# Ondalık ayırıcı her zaman nokta; Python'a özgü "1_000" ve "nan"/"inf" metinleri geçersiz.
INTEGER_TEXT = re.compile(r"[+-]?\d+")
DECIMAL_TEXT = re.compile(r"[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?")


def error_payload(code: str, field: Any, message: str) -> Dict[str, Any]:
    return {"error": message, "code": code, "field": field}


def dumps(payload: Dict[str, Any]) -> str:
    """CLI stdout'u ve MCP metin içeriği için tek satır JSON."""
    return json.dumps(payload, separators=(",", ":"))


def version_payload() -> Dict[str, Any]:
    import scipy

    return {"contract_version": CONTRACT_VERSION, "name": TEAM_NAME,
            "engine": f"Python {platform.python_version()}, scipy {scipy.__version__}"}


def parse_value(field: str, value: Any) -> Any:
    """CLI'dan metin, MCP'den JSON değeri gelir; ikisi de aynı kurala göre çevrilir."""
    if isinstance(value, bool) or value is None:
        raise ContractError(INVALID_VALUE, field, f"{field} bir sayı olmalıdır, alınan: {value}")
    if field in INTEGER_FIELDS:
        if isinstance(value, int):
            return value
        if isinstance(value, str) and INTEGER_TEXT.fullmatch(value.strip()):
            return int(value)
        raise ContractError(INVALID_VALUE, field, f"{field} tam sayı olmalıdır, alınan: {value}")

    if isinstance(value, (int, float)):
        number = float(value)
    elif isinstance(value, str) and DECIMAL_TEXT.fullmatch(value.strip()):
        number = float(value)
    else:
        raise ContractError(INVALID_VALUE, field,
                            f"{field} sonlu bir sayı olmalıdır (NaN/inf olamaz), alınan: {value}")
    if not math.isfinite(number):
        raise ContractError(INVALID_VALUE, field,
                            f"{field} sonlu bir sayı olmalıdır (NaN/inf olamaz), alınan: {value}")
    return number


def _handle(fields: Dict[str, Any]) -> Dict[str, Any]:
    for key in ("test", "mode"):
        if key not in fields:
            raise ContractError(MISSING_PARAM, key, f"Eksik alan: '{key}'")
    test, mode = fields["test"], fields["mode"]
    check_supported(test, mode)

    inputs, outputs = FIELDS[(test, mode)]
    for key in fields:
        if key not in ("test", "mode") and key not in inputs:
            raise ContractError(UNKNOWN_PARAM, key, f"'{key}' alanı {test} / {mode} için tanınmıyor ya da ilgisiz")
    for key in inputs:
        if key not in fields:
            raise ContractError(MISSING_PARAM, key, f"Eksik alan: '{key}' ({test} / {mode} için zorunlu)")

    params = {ENGINE_PARAM.get(key, key): parse_value(key, fields[key]) for key in inputs}
    result = run_power_analysis(test=test, mode=mode, params=params)
    return {name: result[OUTPUT_SOURCE[name]] for name in outputs}


def handle_request(fields: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """Sözleşme isteğini işler: (çıktı sözlüğü, çıkış kodu)."""
    try:
        return _handle(fields), EXIT_OK
    except ContractError as err:
        return error_payload(err.code, err.field, str(err)), EXIT_INVALID_INPUT
    except Exception as err:  # Beklenmeyen durum: iç hata (CONTRACT.md §2.4, çıkış kodu 1)
        return error_payload("INTERNAL", None, f"İç hata: {err}"), EXIT_INTERNAL_ERROR
