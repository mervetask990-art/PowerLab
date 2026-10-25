"""
src/powerlab/engine/distributions.py
Noncentral t (nct) ve merkezi Student-t dağılımı sarmalayıcıları.
Tüm hesaplamalar saf (pure) ve yan etkisizdir.

scipy.stats yerine doğrudan scipy.special kullanılır (stdtrit, nctdtr): scipy.stats.t.ppf ve
scipy.stats.nct.cdf aynı özel fonksiyonları çağırır, ama scipy.stats'ın içe aktarılması tek başına
~1.1 s sürer ve CONTRACT.md §2.1'deki 2 saniye sınırını zorlar.
"""

import math
from typing import Callable

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


def central_alpha(critical_t: float, df: int, tails: int) -> float:
    """Merkezi t altında, kritik değeri aşma olasılığı: tails * (1 - F(t_crit; df))."""
    return float(tails * (1.0 - special.stdtr(df, critical_t)))


def find_root(func: Callable[[float], float], low: float, high: float,
              tolerance: float = 1e-14, max_iter: int = 500) -> float:
    """
    [low, high] aralığında işaret değiştiren monoton bir fonksiyonun kökünü ikiye bölmeyle bulur.
    scipy.optimize kullanılmaz: içe aktarımı CONTRACT.md §2.1'deki 2 saniye sınırını zorlar.
    """
    f_low = func(low)
    if f_low == 0.0:
        return low
    for _ in range(max_iter):
        mid = 0.5 * (low + high)
        f_mid = func(mid)
        if f_mid == 0.0 or (high - low) <= tolerance * max(1.0, abs(mid)):
            return mid
        if (f_mid < 0.0) == (f_low < 0.0):
            low, f_low = mid, f_mid
        else:
            high = mid
    return 0.5 * (low + high)


def expand_upper(func: Callable[[float], float], start: float, want_positive: bool,
                 limit: float = 1e6) -> float:
    """
    Kök aralığının üst ucunu, fonksiyon istenen işarete geçene kadar ikiye katlayarak büyütür.
    Sınır aşılırsa None yerine ValueError fırlatır; çağıran bunu NO_SOLUTION'a çevirir.
    """
    high = start
    while (func(high) > 0.0) != want_positive:
        high *= 2.0
        if high > limit:
            raise ValueError("kök aralığı aşıldı")
    return high


# --- F dağılımı (multireg-r2) ---------------------------------------------------------------------

def f_critical_value(alpha: float, df1: int, df2: int) -> float:
    """Merkezi F'nin (1 - α) yüzdeliği."""
    return float(special.fdtri(df1, df2, 1.0 - alpha))


def f_central_alpha(critical_f: float, df1: int, df2: int) -> float:
    """Merkezi F altında kritik değeri aşma olasılığı."""
    return float(special.fdtrc(df1, df2, critical_f))


def ncf_power(critical_f: float, df1: int, df2: int, ncp: float) -> float:
    """Merkezsiz F altında güç: 1 - F_ncf(critical; df1, df2, λ). NaN durumunda uç değere çekilir."""
    cdf = special.ncfdtr(df1, df2, ncp, critical_f)
    if math.isnan(cdf):
        return 1.0 if ncp > critical_f * df1 else 0.0
    return float(min(max(1.0 - cdf, 0.0), 1.0))
