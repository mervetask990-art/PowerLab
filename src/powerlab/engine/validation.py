"""
src/powerlab/engine/validation.py
Parametre sınırlarını ve tiplerini denetleyen girdi doğrulama kuralları.
Hatalı durumda açıklayıcı ValueError fırlatır.
"""

import math
from typing import Any


def _require_finite(name: str, value: Any) -> float:
    """Değerin sayı olduğunu ve NaN/±inf olmadığını doğrular; float olarak döner."""
    if value is None or isinstance(value, bool):
        raise ValueError(f"{name} değeri bir sayı olmalıdır, alınan: {value}")
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} değeri bir sayı olmalıdır, alınan: {value}") from None
    if not math.isfinite(number):
        raise ValueError(f"{name} değeri sonlu bir sayı olmalıdır (NaN/inf olamaz), alınan: {value}")
    return number


def validate_alpha(alpha: float) -> None:
    alpha = _require_finite("Alpha", alpha)
    if not (0.0 < alpha < 1.0):
        raise ValueError(f"Alpha değeri (0, 1) açık aralığında olmalıdır, alınan: {alpha}")


def validate_power(power: float) -> None:
    power = _require_finite("Power (güç)", power)
    if not (0.0 < power < 1.0):
        raise ValueError(f"Power (güç) değeri (0, 1) açık aralığında olmalıdır, alınan: {power}")


def validate_tails(tails: int) -> None:
    if tails not in (1, 2):
        raise ValueError(f"Kuyruk sayısı (tails) 1 veya 2 olmalıdır, alınan: {tails}")


# A priori'de kabul edilen en küçük |dz|. Kanıt: G*Power dz=0.00001'i kabul ediyor (V42),
# dz=0'ı reddediyor (V25, LEDGER L14). Aradaki değerlerin reddi doğrulanmamış hipotezdir (Q5).
A_PRIORI_MIN_ABS_DZ = 0.00001


def validate_effect_size(dz: float) -> None:
    """dz işaretli olabilir; post hoc'ta 0 da kabul edilir (G*Power V37, V41, V43; LEDGER L13, L16)."""
    _require_finite("Etki büyüklüğü (dz)", dz)


def validate_a_priori_effect_size(dz: float) -> None:
    dz = _require_finite("Etki büyüklüğü (dz)", dz)
    if abs(dz) < A_PRIORI_MIN_ABS_DZ:
        raise ValueError(
            f"A priori analizde etki büyüklüğünün (dz) mutlak değeri en az {A_PRIORI_MIN_ABS_DZ:.5f} olmalıdır, alınan: {dz}"
        )


def validate_power_not_below_alpha(power: float, alpha: float) -> None:
    """Güç = alpha kabul edilir (G*Power V16); güç < alpha hata (V17, LEDGER L12)."""
    if power < alpha:
        raise ValueError(
            f"Power (güç) alpha değerinden küçük olamaz (power >= alpha olmalıdır), alınan: power={power}, alpha={alpha}"
        )


def validate_sample_size(n: Any, min_n: int = 2) -> None:
    number = _require_finite("Örneklem büyüklüğü (n)", n)
    if number != int(number):
        raise ValueError(f"Örneklem büyüklüğü (n) tamsayı olmalıdır, alınan: {n}")
    if number < min_n:
        raise ValueError(f"Örneklem büyüklüğü (n) izin verilen aralığın dışında: en az {min_n} olmalıdır, alınan: {n}")
