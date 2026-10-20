"""
src/powerlab/engine/rounding.py
Yuvarlama, tamsayı N dönüşümü ve grup oran dağıtım kuralları.
"""

import math
from typing import Tuple

# Çıktıdaki float alanların ondalık basamak sayısı. Tek kaynak budur.
# Kanıt: G*Power 3.1.9.7 Output Parameters paneli 7 ondalık gösterir (oracle/screenshots/V01.png);
# gerekçe: CONTRACT_ASSUMED.md D1-D3.
OUTPUT_DECIMALS = 7


def ceil_to_int(value: float) -> int:
    """Float değeri yukarı tamsayıya yuvarlar."""
    return int(math.ceil(value))


def round_result_dict(d: dict, precision: int = OUTPUT_DECIMALS) -> dict:
    """Sözlükteki float değerleri belirtilen basamağa yuvarlar."""
    res = {}
    for k, v in d.items():
        if isinstance(v, float):
            res[k] = round(v, precision)
        else:
            res[k] = v
    return res
