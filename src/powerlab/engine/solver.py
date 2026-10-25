"""
src/powerlab/engine/solver.py
Çözücü yönlendirme ve aile kayıt defteri (Family Registry).
CLI ve MCP yalnızca buradaki saf fonksiyonları (powerlab.engine.contract üzerinden) çağırır.
Test ve mod kimlikleri CONTRACT.md §3 ve §4'teki gibi birebirdir; takma ad yoktur.
"""

from typing import Any, Dict

from powerlab.engine.errors import UNSUPPORTED, ContractError
from powerlab.engine.families import t_paired

# Uygulanan (test, mod) çiftleri ve çözücüleri.
IMPLEMENTED = {
    ("t-paired", "a-priori"): t_paired.solve_n,
    ("t-paired", "post-hoc"): t_paired.compute_power,
    ("t-paired", "compromise"): t_paired.compromise,
    ("t-paired", "criterion"): t_paired.criterion,
    ("t-paired", "sensitivity"): t_paired.sensitivity,
}

# CONTRACT.md'de tanımlı ama bu motorda uygulanmamış kimlikler de UNSUPPORTED döner.
CONTRACT_TESTS = ("t2-indep", "t-paired", "anova-oneway", "chi2-contingency", "multireg-r2")
CONTRACT_MODES = ("a-priori", "post-hoc", "compromise", "criterion", "sensitivity")


def check_supported(test: Any, mode: Any) -> None:
    if test not in CONTRACT_TESTS:
        raise ContractError(UNSUPPORTED, "test", f"Bilinmeyen test: '{test}'. Geçerli: {list(CONTRACT_TESTS)}")
    if mode not in CONTRACT_MODES:
        raise ContractError(UNSUPPORTED, "mode", f"Bilinmeyen mod: '{mode}'. Geçerli: {list(CONTRACT_MODES)}")
    if not any(t == test for t, _ in IMPLEMENTED):
        raise ContractError(UNSUPPORTED, "test", f"{test} bu motorda henüz uygulanmadı")
    if (test, mode) not in IMPLEMENTED:
        raise ContractError(UNSUPPORTED, "mode", f"{test} için {mode} modu bu motorda henüz uygulanmadı")


def run_power_analysis(test: str, mode: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Belirtilen test ailesi ve moda göre hesaplamayı çalıştırır.
    mode: 'a-priori' -> solve_n, 'post-hoc' -> compute_power
    Dönüş, motorun iç sözlüğüdür (n, df, ncp, critical, actual_power); sözleşme alanlarına
    powerlab.engine.contract eşler.
    """
    check_supported(test, mode)
    return IMPLEMENTED[(test, mode)](params)
