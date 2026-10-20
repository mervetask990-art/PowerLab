"""
src/powerlab/engine/validation.py
Parametre sınırlarını ve tiplerini denetleyen girdi doğrulama kuralları.
Hatalı durumda açıklayıcı ValueError fırlatır.
"""

from typing import Optional


def validate_alpha(alpha: float) -> None:
    if alpha is None or not (0.0 < alpha < 1.0):
        raise ValueError(f"Alpha değeri (0, 1) açık aralığında olmalıdır, alınan: {alpha}")


def validate_power(power: float) -> None:
    if power is None or not (0.0 < power < 1.0):
        raise ValueError(f"Power (güç) değeri (0, 1) açık aralığında olmalıdır, alınan: {power}")


def validate_tails(tails: int) -> None:
    if tails not in (1, 2):
        raise ValueError(f"Kuyruk sayısı (tails) 1 veya 2 olmalıdır, alınan: {tails}")


def validate_effect_size(dz: float) -> None:
    if dz is None or dz <= 0.0:
        raise ValueError(f"Etki büyüklüğü (dz) kesinlikle pozitif (> 0) olmalıdır, alınan: {dz}")


def validate_sample_size(n: int, min_n: int = 2) -> None:
    if n is None or n < min_n:
        raise ValueError(f"Örneklem büyüklüğü (n) en az {min_n} olmalıdır, alınan: {n}")
