"""
src/powerlab/engine/solver.py
Çözücü yönlendirme ve aile kayıt defteri (Family Registry).
CLI ve MCP yalnızca buradaki saf fonksiyonları çağırır.
"""

from typing import Dict, Any
from powerlab.engine.families import t_paired

FAMILY_REGISTRY = {
    "t-paired": t_paired,
    "t_paired": t_paired,
}


def run_power_analysis(test: str, mode: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Belirtilen test ailesi ve moda göre hesaplamayı çalıştırır.
    mode: 'a-priori' (veya 'a_priori') -> solve_n
          'post-hoc' (veya 'post_hoc') -> compute_power
    """
    clean_test = test.strip().lower().replace("_", "-")
    if clean_test not in FAMILY_REGISTRY:
        supported = list(FAMILY_REGISTRY.keys())
        raise ValueError(f"Desteklenmeyen test ailesi: '{test}'. Desteklenenler: {supported}")

    family_module = FAMILY_REGISTRY[clean_test]
    clean_mode = mode.strip().lower().replace("_", "-")

    if clean_mode in ("a-priori", "apriori"):
        return family_module.solve_n(params)
    elif clean_mode in ("post-hoc", "posthoc"):
        return family_module.compute_power(params)
    else:
        raise ValueError(f"Geçersiz analiz modu: '{mode}'. 'a-priori' veya 'post-hoc' bekleniyor.")
