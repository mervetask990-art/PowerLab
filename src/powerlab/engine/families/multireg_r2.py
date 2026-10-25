"""
src/powerlab/engine/families/multireg_r2.py
Çoklu doğrusal regresyon, sabit model, R² sıfırdan sapma (Linear multiple regression: Fixed model,
R² deviation from zero). Bonus aile, CONTRACT.md §4.5.

Model (Faul et al., 2009; LEDGER [DOK]): λ = f²·N, df1 = yordayıcı sayısı (k), df2 = N − k − 1.
Kritik F merkezi F'den, güç merkezsiz F'den. Saf fonksiyonlardır; varsayılan değer yoktur, çıktı tam
double'dır. Kâhin: oracle/gpower_multireg.csv (M01–M28) ve CONTRACT.md §9.
"""

from typing import Any, Dict

from powerlab.engine.distributions import (
    expand_upper,
    f_central_alpha,
    f_critical_value,
    find_root,
    ncf_power,
)
from powerlab.engine.errors import MISSING_PARAM, NO_SOLUTION, ContractError
from powerlab.engine.validation import (
    validate_alpha,
    validate_beta_alpha_ratio,
    validate_f2,
    validate_n_for_predictors,
    validate_power,
    validate_power_not_below_alpha,
    validate_predictors,
)

CONTRACT_FIELD = {"n": "n_total"}
_BRACKET_LIMIT = 1e6


def _require(params: Dict[str, Any], key: str) -> Any:
    if params.get(key) is None:
        raise ContractError(MISSING_PARAM, CONTRACT_FIELD.get(key, key), f"Eksik parametre: '{key}'")
    return params[key]


def _expand_upper(func, start: float, want_positive: bool) -> float:
    try:
        return expand_upper(func, start, want_positive, _BRACKET_LIMIT)
    except ValueError:
        raise ContractError(NO_SOLUTION, None, "Bu girdilerle çözüm bulunamadı (kök aralığı aşıldı).") from None


def _evaluate(f2: float, n: int, k: int, alpha: float) -> Dict[str, Any]:
    df1, df2 = k, n - k - 1
    ncp = f2 * n
    critical = f_critical_value(alpha, df1, df2)
    return {"n": n, "df1": df1, "df2": df2, "ncp": ncp, "critical": critical,
            "actual_power": ncf_power(critical, df1, df2, ncp)}


def solve_n(params: Dict[str, Any]) -> Dict[str, Any]:
    """A priori: gücün hedefe ulaştığı en küçük tamsayı N (en az k + 2; kâhin M13)."""
    f2 = _require(params, "f2")
    alpha = _require(params, "alpha")
    target = _require(params, "power")
    k = _require(params, "predictors")

    validate_f2(f2, a_priori=True)
    validate_alpha(alpha)
    validate_power(target)
    validate_predictors(k)
    f2, alpha, target, k = float(f2), float(alpha), float(target), int(k)
    validate_power_not_below_alpha(target, alpha)

    low = k + 2
    if _evaluate(f2, low, k, alpha)["actual_power"] >= target:
        return _evaluate(f2, low, k, alpha)
    high = low * 2
    while _evaluate(f2, high, k, alpha)["actual_power"] < target:
        high *= 2
    while low + 1 < high:  # değişmez: güç(low) < hedef <= güç(high)
        mid = (low + high) // 2
        if _evaluate(f2, mid, k, alpha)["actual_power"] >= target:
            high = mid
        else:
            low = mid
    return _evaluate(f2, high, k, alpha)


def compute_power(params: Dict[str, Any]) -> Dict[str, Any]:
    """Post hoc: verilen N'de güç."""
    f2 = _require(params, "f2")
    alpha = _require(params, "alpha")
    n = _require(params, "n")
    k = _require(params, "predictors")

    validate_f2(f2, a_priori=False)
    validate_alpha(alpha)
    validate_predictors(k)
    validate_n_for_predictors(n, int(k))
    return _evaluate(float(f2), int(n), int(k), float(alpha))


def compromise(params: Dict[str, Any]) -> Dict[str, Any]:
    """Compromise: β = (β/α oranı)·α eşitliğini sağlayan kritik F; α, β ve güç."""
    f2 = _require(params, "f2")
    ratio = _require(params, "beta_alpha_ratio")
    n = _require(params, "n")
    k = _require(params, "predictors")

    validate_f2(f2, a_priori=False)
    validate_beta_alpha_ratio(ratio)
    validate_predictors(k)
    validate_n_for_predictors(n, int(k))
    f2, ratio, n, k = float(f2), float(ratio), int(n), int(k)

    df1, df2 = k, n - k - 1
    ncp = f2 * n

    def excess_beta(critical: float) -> float:
        return (1.0 - ncf_power(critical, df1, df2, ncp)) - ratio * f_central_alpha(critical, df1, df2)

    critical = find_root(excess_beta, 0.0, _expand_upper(excess_beta, 10.0, want_positive=True))
    power = ncf_power(critical, df1, df2, ncp)
    return {"n": n, "df1": df1, "df2": df2, "ncp": ncp, "critical": critical,
            "alpha": f_central_alpha(critical, df1, df2), "beta": 1.0 - power, "actual_power": power}


def criterion(params: Dict[str, Any]) -> Dict[str, Any]:
    """Criterion: gücü hedefe eşitleyen kritik F ve buna karşılık gelen α."""
    f2 = _require(params, "f2")
    target = _require(params, "power")
    n = _require(params, "n")
    k = _require(params, "predictors")

    validate_f2(f2, a_priori=False)
    validate_power(target)
    validate_predictors(k)
    validate_n_for_predictors(n, int(k))
    f2, target, n, k = float(f2), float(target), int(n), int(k)

    df1, df2 = k, n - k - 1
    ncp = f2 * n

    def power_gap(critical: float) -> float:
        return ncf_power(critical, df1, df2, ncp) - target

    critical = find_root(power_gap, 0.0, _expand_upper(power_gap, 10.0, want_positive=False))
    return {"n": n, "df1": df1, "df2": df2, "ncp": ncp, "critical": critical,
            "alpha": f_central_alpha(critical, df1, df2)}


def sensitivity(params: Dict[str, Any]) -> Dict[str, Any]:
    """Sensitivity: α, güç ve N verildiğinde gücü hedefe eşitleyen en küçük f²."""
    alpha = _require(params, "alpha")
    target = _require(params, "power")
    n = _require(params, "n")
    k = _require(params, "predictors")

    validate_alpha(alpha)
    validate_power(target)
    validate_predictors(k)
    validate_n_for_predictors(n, int(k))
    alpha, target, n, k = float(alpha), float(target), int(n), int(k)
    validate_power_not_below_alpha(target, alpha)

    df1, df2 = k, n - k - 1
    critical = f_critical_value(alpha, df1, df2)

    def power_gap(f2: float) -> float:
        return ncf_power(critical, df1, df2, f2 * n) - target

    f2 = find_root(power_gap, 0.0, _expand_upper(power_gap, 1.0, want_positive=True))
    return {"n": n, "df1": df1, "df2": df2, "ncp": f2 * n, "critical": critical, "f2": f2}
