"""
src/powerlab/engine/families/t_paired.py
Eşleştirilmiş iki bağımlı grup t-testi (Means: Difference between two dependent means / matched pairs).
Mimaride her aile compute_power(params) ve solve_n(params) arayüzünü uygular.
Saf fonksiyonlardır, yan etki barındırmaz.

dz > 0 olmalıdır (CONTRACT.md §5). G*Power negatif dz'yi kabul edip δ ve critical'ı işaretli
verir (LEDGER L13); sözleşme bunu reddeder. Varsayılan değer yoktur (CONTRACT.md §2.1).
Çıktı tam double'dır, yuvarlanmaz (CONTRACT.md §2.3).
"""

import math
from typing import Dict, Any

from powerlab.engine.distributions import t_critical_value, nct_power
from powerlab.engine.errors import MISSING_PARAM, ContractError
from powerlab.engine.validation import (
    validate_alpha,
    validate_power,
    validate_tails,
    validate_effect_size,
    validate_a_priori_effect_size,
    validate_post_hoc_effect_size,
    validate_power_not_below_alpha,
    validate_sample_size,
)

# Motorun iç parametre adı -> sözleşmedeki alan adı (CONTRACT.md §4.2).
CONTRACT_FIELD = {"n": "n_total"}


def _require(params: Dict[str, Any], key: str) -> Any:
    if params.get(key) is None:
        raise ContractError(MISSING_PARAM, CONTRACT_FIELD.get(key, key), f"Eksik parametre: '{key}'")
    return params[key]


def compute_power(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Post-hoc analiz: Verilen n, dz, alpha ve tails parametreleriyle gerçekleşen gücü hesaplar.
    """
    tails = _require(params, "tails")
    dz = _require(params, "dz")
    alpha = _require(params, "alpha")
    n = _require(params, "n")

    validate_tails(tails)
    validate_effect_size(dz)
    validate_post_hoc_effect_size(dz)
    validate_alpha(alpha)
    # Post hoc alt sınırı 3: G*Power N=1 ve N=2'yi reddediyor (V29, V40; [REA] 0x4dc2a0, LEDGER L20).
    validate_sample_size(n, min_n=3)
    tails, dz, alpha, n = int(tails), float(dz), float(alpha), int(n)

    df = n - 1
    ncp = dz * math.sqrt(n)
    t_crit = t_critical_value(alpha=alpha, df=df, tails=tails)
    power = nct_power(critical_t=t_crit, df=df, ncp=ncp, tails=tails)

    return {"n": n, "actual_power": power, "critical": t_crit, "df": df, "ncp": ncp}


def solve_n(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    A priori analiz: Verilen dz, alpha, target_power ve tails parametreleriyle
    hedef güce (Power >= target_power) ulaşan en küçük tamsayı N değerini bulur.
    G*Power sürekli N için kök bulup 1e-10'a yuvarlayarak tavanını alır ([REA] 0x496aa0, LEDGER L21);
    güç N'de monoton olduğu sürece bu tamsayı araması aynı N'yi verir.
    """
    tails = _require(params, "tails")
    dz = _require(params, "dz")
    alpha = _require(params, "alpha")
    target_power = _require(params, "power")

    # Sıra G*Power'daki gibi: dz eşiği -> α -> güç -> α <= güç ([REA] LEDGER L32).
    validate_tails(tails)
    validate_effect_size(dz)
    validate_a_priori_effect_size(dz)
    validate_alpha(alpha)
    validate_power(target_power)
    tails, dz, alpha, target_power = int(tails), float(dz), float(alpha), float(target_power)
    validate_power_not_below_alpha(target_power, alpha)

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

    return {"n": best_n, "actual_power": actual_power, "critical": t_crit, "df": df, "ncp": ncp}
