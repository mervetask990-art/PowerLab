"""
src/powerlab/engine/distributions.py
Noncentral t (nct) ve merkezi Student-t dağılımı sarmalayıcıları.
Tüm hesaplamalar saf (pure) ve yan etkisizdir.

scipy.stats yerine doğrudan scipy.special kullanılır (stdtrit, nctdtr): scipy.stats.t.ppf ve
scipy.stats.nct.cdf aynı özel fonksiyonları çağırır, ama scipy.stats'ın içe aktarılması tek başına
~1.1 s sürer ve CONTRACT.md §2.1'deki 2 saniye sınırını zorlar.
"""

import math

from scipy import special


def t_critical_value(alpha: float, df: int, tails: int = 2) -> float:
    """
    Kritik t değerini (t_crit) hesaplar.
    tails=2: t_(1 - alpha/2, df)
    tails=1: t_(1 - alpha, df)
    """
    if tails not in (1, 2):
        raise ValueError(f"Kuyruk sayısı 1 veya 2 olmalıdır, alınan: {tails}")
    if df < 1:
        raise ValueError(f"Serbestlik derecesi df >= 1 olmalıdır, alınan: {df}")
    if not (0.0 < alpha < 1.0):
        raise ValueError(f"Alpha (0, 1) aralığında olmalıdır, alınan: {alpha}")

    prob = 1.0 - (alpha / 2.0 if tails == 2 else alpha)
    return float(special.stdtrit(df, prob))


def nct_power(critical_t: float, df: int, ncp: float, tails: int = 2) -> float:
    """
    Noncentral t dağılımı altında gücü hesaplar.
    tails=1: 1 - CDF(t_crit; df, ncp)
    tails=2: (1 - CDF(t_crit; df, ncp)) + CDF(-t_crit; df, ncp)
             G*Power çift kuyrukta sol kuyruk integralini de toplar.
    """
    if df < 1:
        raise ValueError(f"df >= 1 olmalıdır, alınan: {df}")

    if tails == 1:
        power = 1.0 - special.nctdtr(df, ncp, critical_t)
        if math.isnan(power):
            power = 1.0 if ncp > critical_t else 0.0
    elif tails == 2:
        right_tail = 1.0 - special.nctdtr(df, ncp, critical_t)
        if math.isnan(right_tail):
            right_tail = 1.0 if ncp > critical_t else 0.0

        # Sol kuyruk: ncp pozitif ve büyük olduğunda sol kuyruk integralinde scipy NaN üretebilir
        left_tail = special.nctdtr(df, ncp, -critical_t)
        if math.isnan(left_tail):
            left_tail = 0.0

        power = right_tail + left_tail
    else:
        raise ValueError(f"Kuyruk sayısı 1 veya 2 olmalıdır, alınan: {tails}")

    # Sayısal taşmaları [0, 1] aralığına kırp
    return float(min(max(power, 0.0), 1.0))
