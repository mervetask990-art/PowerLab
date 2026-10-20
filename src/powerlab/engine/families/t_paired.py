"""
src/powerlab/engine/families/t_paired.py
Eşleştirilmiş iki bağımlı grup t-testi (Means: Difference between two dependent means / matched pairs).
Mimaride her aile compute_power(params) ve solve_n(params) arayüzünü uygular.
Saf fonksiyonlardır, yan etki barındırmaz.
"""

import math
from typing import Dict, Any

from powerlab.engine.distributions import t_critical_value, nct_power
from powerlab.engine.validation import (
    validate_alpha,
    validate_power,
    validate_tails,
    validate_effect_size,
    validate_sample_size,
)
from powerlab.engine.rounding import round_result_dict


def compute_power(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Post-hoc analiz: Verilen n, dz, alpha ve tails parametreleriyle gerçekleşen gücü hesaplar.
    """
    tails = int(params.get("tails", 2))
    dz = float(params["dz"])
    alpha = float(params["alpha"])
    n = int(params["n"])

    validate_tails(tails)
    validate_effect_size(dz)
    validate_alpha(alpha)
    validate_sample_size(n, min_n=2)

    df = n - 1
    ncp = dz * math.sqrt(n)
    t_crit = t_critical_value(alpha=alpha, df=df, tails=tails)
    power = nct_power(critical_t=t_crit, df=df, ncp=ncp, tails=tails)

    res = {
        "n": n,
        "n_total": n,
        "actual_power": power,
        "critical": t_crit,
        "df": df,
        "ncp": ncp,
    }
    return round_result_dict(res, precision=6)


def solve_n(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    A priori analiz: Verilen dz, alpha, target_power ve tails parametreleriyle
    hedef güce (Power >= target_power) ulaşan en küçük tamsayı N değerini bulur.
    Durma koşulu (Power(N) >= target_power olan en küçük tamsayı N) bir VARSAYIMDIR
    (LEDGER L06, [AJAN]); G*Power ile aynı olduğu henüz doğrulanmadı.
    """
    tails = int(params.get("tails", 2))
    dz = float(params["dz"])
    alpha = float(params["alpha"])
    target_power = float(params["power"])

    validate_tails(tails)
    validate_effect_size(dz)
    validate_alpha(alpha)
    validate_power(target_power)

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
        "critical": t_crit,
        "df": df,
        "ncp": ncp,
    }
    return round_result_dict(res, precision=6)
