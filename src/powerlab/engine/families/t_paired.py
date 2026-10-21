"""
src/powerlab/engine/families/t_paired.py
Eşleştirilmiş iki bağımlı grup t-testi (Means: Difference between two dependent means / matched pairs).
Mimaride her aile compute_power(params) ve solve_n(params) arayüzünü uygular.
Saf fonksiyonlardır, yan etki barındırmaz.

dz işaretlidir: N ve güç |dz| ile hesaplanır; ncp = dz * sqrt(N) ve critical, dz'nin işaretini
taşır (dz = 0 için +). Kanıt: G*Power V21, V26, V37 (LEDGER L13).
"""

import math
from typing import Dict, Any

from powerlab.engine.distributions import t_critical_value, nct_power
from powerlab.engine.validation import (
    validate_alpha,
    validate_power,
    validate_tails,
    validate_effect_size,
    validate_a_priori_effect_size,
    validate_power_not_below_alpha,
    validate_sample_size,
)
from powerlab.engine.rounding import round_result_dict


def _require(params: Dict[str, Any], key: str) -> Any:
    if params.get(key) is None:
        raise ValueError(f"Eksik parametre: '{key}'")
    return params[key]


def _sign(dz: float) -> float:
    return -1.0 if dz < 0 else 1.0


def compute_power(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Post-hoc analiz: Verilen n, dz, alpha ve tails parametreleriyle gerçekleşen gücü hesaplar.
    """
    tails = params.get("tails", 2)
    dz = _require(params, "dz")
    alpha = _require(params, "alpha")
    n = _require(params, "n")

    validate_tails(tails)
    validate_effect_size(dz)
    validate_alpha(alpha)
    # Post hoc alt sınırı 3: G*Power N=1 ve N=2'yi reddediyor (V29, V40; LEDGER L15).
    validate_sample_size(n, min_n=3)
    tails, dz, alpha, n = int(tails), float(dz), float(alpha), int(n)

    df = n - 1
    t_crit = t_critical_value(alpha=alpha, df=df, tails=tails)
    power = nct_power(critical_t=t_crit, df=df, ncp=abs(dz) * math.sqrt(n), tails=tails)

    res = {
        "n": n,
        "n_total": n,
        "actual_power": power,
        "critical": _sign(dz) * t_crit,
        "df": df,
        "ncp": dz * math.sqrt(n),
    }
    return round_result_dict(res)


def solve_n(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    A priori analiz: Verilen dz, alpha, target_power ve tails parametreleriyle
    hedef güce (Power >= target_power) ulaşan en küçük tamsayı N değerini bulur.
    Durma koşulu (Power(N) >= target_power olan en küçük tamsayı N) bir VARSAYIMDIR
    (LEDGER L06, [AJAN]); G*Power ile aynı olduğu henüz doğrulanmadı.
    """
    tails = params.get("tails", 2)
    dz = _require(params, "dz")
    alpha = _require(params, "alpha")
    target_power = _require(params, "power")

    validate_tails(tails)
    validate_effect_size(dz)
    validate_alpha(alpha)
    validate_power(target_power)
    validate_a_priori_effect_size(dz)
    tails, dz, alpha, target_power = int(tails), float(dz), float(alpha), float(target_power)
    validate_power_not_below_alpha(target_power, alpha)
    sign, dz = _sign(dz), abs(dz)

    # İkili arama (Binary search) veya monotonik tarama
    # N artarken df ve ncp monotonik artar, dolayısıyla güç de monotonik artar.
    low = 2
    high = 100_000
    
    # Üst sınırı dinamik genişlet (aşırı küçük dz durumları için)
    while True:
        df_high = high - 1
        ncp_high = dz * math.sqrt(high)
        tc_high = t_critical_value(alpha=alpha, df=df_high, tails=tails)
        p_high = nct_power(critical_t=tc_high, df=df_high, ncp=ncp_high, tails=tails)
        if p_high >= target_power:
            break
        high *= 2

    best_n = high
    while low <= high:
        mid = (low + high) // 2
        df = mid - 1
        ncp = dz * math.sqrt(mid)
        t_crit = t_critical_value(alpha=alpha, df=df, tails=tails)
        pwr = nct_power(critical_t=t_crit, df=df, ncp=ncp, tails=tails)

        if pwr >= target_power:
            best_n = mid
            high = mid - 1  # Daha küçük bir tamsayı N ile de sağlanıyor mu ara
        else:
            low = mid + 1

    # Bulunan en küçük tamsayı N için tam metrikleri hesapla
    df = best_n - 1
    ncp = dz * math.sqrt(best_n)
    t_crit = t_critical_value(alpha=alpha, df=df, tails=tails)
    actual_power = nct_power(critical_t=t_crit, df=df, ncp=ncp, tails=tails)

    res = {
        "n": best_n,
        "n_total": best_n,
        "actual_power": actual_power,
        "critical": sign * t_crit,
        "df": df,
        "ncp": sign * ncp,
    }
    return round_result_dict(res)
