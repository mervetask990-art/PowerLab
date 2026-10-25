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


# α ve güç için G*Power'ın kabul aralığı (kapalı): [REA] 0x487530 / 0x488110, LEDGER L32.
# CONTRACT.md §5'in (0, 1) aralığının içindedir.
PROBABILITY_MIN = 1e-7
PROBABILITY_MAX = 0.9999999


def validate_alpha(alpha: float) -> None:
    alpha = _require_finite("Alpha", "alpha", alpha)
    if not (PROBABILITY_MIN <= alpha <= PROBABILITY_MAX):
        raise ContractError(
            OUT_OF_RANGE, "alpha",
            f"Alpha değeri [{PROBABILITY_MIN:g}, {PROBABILITY_MAX}] aralığında olmalıdır, alınan: {alpha}",
        )


def validate_power(power: float) -> None:
    power = _require_finite("Power (güç)", "power", power)
    if not (PROBABILITY_MIN <= power <= PROBABILITY_MAX):
        raise ContractError(
            OUT_OF_RANGE, "power",
            f"Power (güç) değeri [{PROBABILITY_MIN:g}, {PROBABILITY_MAX}] aralığında olmalıdır, alınan: {power}",
        )


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


# Post hoc'ta etki büyüklüğü üst sınırı (kapalı): [REA] 0x487b70, LEDGER L33. A priori'de üst sınır yok.
POST_HOC_MAX_DZ = 20.0


def validate_post_hoc_effect_size(dz: float) -> None:
    dz = _require_finite("Etki büyüklüğü (dz)", "dz", dz)
    if dz > POST_HOC_MAX_DZ:
        raise ContractError(
            OUT_OF_RANGE, "dz",
            f"Post hoc analizde etki büyüklüğü (dz) en çok {POST_HOC_MAX_DZ:g} olabilir, alınan: {dz}",
        )


def validate_beta_alpha_ratio(ratio: Any) -> None:
    """CONTRACT.md §5: beta_alpha_ratio > 0."""
    ratio = _require_finite("β/α oranı", "beta_alpha_ratio", ratio)
    if ratio <= 0.0:
        raise ContractError(OUT_OF_RANGE, "beta_alpha_ratio",
                            f"β/α oranı pozitif olmalıdır (> 0), alınan: {ratio}")


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


# --- multireg-r2 (CONTRACT.md §4.5) ---------------------------------------------------------------
# f² aralığı: CONTRACT.md §5 f2 > 0. G*Power'ın kabul ettiği üst sınır 50; a priori'de alt sınır 1e-06
# (kâhin gözlemi: M15/M28 hata mesajları, oracle/gpower_multireg.csv). Post hoc'ta G*Power f² = 0'ı
# kabul eder (M25); sözleşme reddeder.
F2_MAX = 50.0
A_PRIORI_MIN_F2 = 1e-06


def validate_f2(f2: Any, a_priori: bool) -> None:
    f2 = _require_finite("Etki büyüklüğü (f²)", "f2", f2)
    if f2 <= 0.0:
        raise ContractError(OUT_OF_RANGE, "f2", f"Etki büyüklüğü (f²) pozitif olmalıdır (f2 > 0), alınan: {f2}")
    if a_priori and f2 < A_PRIORI_MIN_F2:
        raise ContractError(OUT_OF_RANGE, "f2", f"A priori analizde f² en az {A_PRIORI_MIN_F2:g} olmalıdır, alınan: {f2}")
    if f2 > F2_MAX:
        raise ContractError(OUT_OF_RANGE, "f2", f"Etki büyüklüğü (f²) en çok {F2_MAX:g} olabilir, alınan: {f2}")


def validate_predictors(predictors: Any) -> None:
    """CONTRACT.md §5: predictors >= 1 (G*Power M16: "There must be at least 1 predictor.")."""
    k = _require_integer("Yordayıcı sayısı", "predictors", predictors)
    if k < 1:
        raise ContractError(OUT_OF_RANGE, "predictors", f"En az 1 yordayıcı olmalıdır, alınan: {k}")


def validate_n_for_predictors(n: Any, predictors: int) -> None:
    """N >= yordayıcı + 2 (df2 >= 1). Kâhin: M26 reddedilir, M27 kabul edilir."""
    number = _require_integer("Örneklem büyüklüğü (n)", "n_total", n)
    if number < predictors + 2:
        raise ContractError(
            OUT_OF_RANGE, "n_total",
            f"Örneklem büyüklüğü yordayıcı sayısı + 2'den küçük olamaz (en az {predictors + 2}), alınan: {n}",
        )
