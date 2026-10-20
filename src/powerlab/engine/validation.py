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


def validate_effect_size(dz: float) -> None:
    dz = _require_finite("Etki büyüklüğü (dz)", dz)
    if dz <= 0.0:
        raise ValueError(f"Etki büyüklüğü (dz) kesinlikle pozitif (> 0) olmalıdır, alınan: {dz}")


def validate_sample_size(n: Any, min_n: int = 2) -> None:
    number = _require_finite("Örneklem büyüklüğü (n)", n)
    if number != int(number):
        raise ValueError(f"Örneklem büyüklüğü (n) tamsayı olmalıdır, alınan: {n}")
    if number < min_n:
        raise ValueError(f"Örneklem büyüklüğü (n) en az {min_n} olmalıdır, alınan: {n}")
