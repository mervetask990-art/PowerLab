"""
src/powerlab/engine/validation.py
Parametre sınırlarını ve tiplerini denetleyen girdi doğrulama kuralları.
Hatalı durumda CONTRACT.md §2.4 kodunu taşıyan ContractError (bir ValueError) fırlatır.
Aralıklar CONTRACT.md §5; aralık içindeki retler G*Power davranışıdır (LEDGER [REA] satırları).
"""

import math
from typing import Any

from powerlab.engine.errors import INCONSISTENT, INVALID_VALUE, OUT_OF_RANGE, ContractError


def _require_finite(name: str, field: str, value: Any) -> float:
    """Değerin sayı olduğunu ve NaN/±inf olmadığını doğrular; float olarak döner."""
    if value is None or isinstance(value, bool):
        raise ContractError(INVALID_VALUE, field, f"{name} değeri bir sayı olmalıdır, alınan: {value}")
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ContractError(INVALID_VALUE, field, f"{name} değeri bir sayı olmalıdır, alınan: {value}") from None
    if not math.isfinite(number):
        raise ContractError(INVALID_VALUE, field,
                            f"{name} değeri sonlu bir sayı olmalıdır (NaN/inf olamaz), alınan: {value}")
    return number


def _require_integer(name: str, field: str, value: Any) -> int:
    number = _require_finite(name, field, value)
    if number != int(number):
        raise ContractError(INVALID_VALUE, field, f"{name} tamsayı olmalıdır, alınan: {value}")
    return int(number)


def validate_alpha(alpha: float) -> None:
    alpha = _require_finite("Alpha", "alpha", alpha)
    if not (0.0 < alpha < 1.0):
        raise ContractError(OUT_OF_RANGE, "alpha", f"Alpha değeri (0, 1) açık aralığında olmalıdır, alınan: {alpha}")


def validate_power(power: float) -> None:
    power = _require_finite("Power (güç)", "power", power)
    if not (0.0 < power < 1.0):
        raise ContractError(OUT_OF_RANGE, "power", f"Power (güç) değeri (0, 1) açık aralığında olmalıdır, alınan: {power}")


def validate_tails(tails: Any) -> None:
    tails = _require_integer("Kuyruk sayısı (tails)", "tails", tails)
    if tails not in (1, 2):
        raise ContractError(OUT_OF_RANGE, "tails", f"Kuyruk sayısı (tails) 1 veya 2 olmalıdır, alınan: {tails}")


def validate_effect_size(dz: float) -> None:
    """CONTRACT.md §5: dz > 0. G*Power negatif dz ve post hoc dz = 0 ile hesap yapar (LEDGER L13, L16);
    sözleşme bunları reddeder."""
    dz = _require_finite("Etki büyüklüğü (dz)", "dz", dz)
    if dz <= 0.0:
        raise ContractError(OUT_OF_RANGE, "dz", f"Etki büyüklüğü (dz) pozitif olmalıdır (dz > 0), alınan: {dz}")


# A priori'de kabul edilen en küçük dz. Kanıt: [REA] 0x4db990 kesin küçük karşılaştırma
# (LEDGER L18); G*Power dz=0.00001'i kabul ediyor (V42).
A_PRIORI_MIN_DZ = 0.00001


def validate_a_priori_effect_size(dz: float) -> None:
    dz = _require_finite("Etki büyüklüğü (dz)", "dz", dz)
    if dz < A_PRIORI_MIN_DZ:
        raise ContractError(
            OUT_OF_RANGE, "dz",
            f"A priori analizde etki büyüklüğü (dz) en az {A_PRIORI_MIN_DZ:.5f} olmalıdır, alınan: {dz}",
        )


def validate_power_not_below_alpha(power: float, alpha: float) -> None:
    """Güç = alpha kabul edilir (G*Power V16); güç < alpha hata ([REA] 0x4880e0, LEDGER L19)."""
    if power < alpha:
        raise ContractError(
            INCONSISTENT, "power",
            f"Power (güç) alpha değerinden küçük olamaz (power >= alpha olmalıdır), alınan: power={power}, alpha={alpha}",
        )


def validate_sample_size(n: Any, min_n: int = 2) -> None:
    number = _require_integer("Örneklem büyüklüğü (n)", "n_total", n)
    if number < min_n:
        raise ContractError(
            OUT_OF_RANGE, "n_total",
            f"Örneklem büyüklüğü (n) izin verilen aralığın dışında: en az {min_n} olmalıdır, alınan: {n}",
        )
