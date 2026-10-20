"""
src/powerlab/engine/rounding.py
Yuvarlama, tamsayı N dönüşümü ve grup oran dağıtım kuralları.
"""

import math
from typing import Tuple


def ceil_to_int(value: float) -> int:
    """Float değeri yukarı tamsayıya yuvarlar."""
    return int(math.ceil(value))


def round_result_dict(d: dict, precision: int = 6) -> dict:
    """Sözlükteki float değerleri belirtilen basamağa yuvarlar."""
    res = {}
    for k, v in d.items():
        if isinstance(v, float):
            res[k] = round(v, precision)
        else:
            res[k] = v
    return res
