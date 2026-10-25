"""
src/powerlab/agent/grounding.py
Değer kaynağı denetimi (CONTRACT.md §10): modelin araca verdiği her sayısal değer ve kuyruk sayısı,
kullanıcının yazdığı metinde ya da kullanıcının açıkça onayladığı bir öneride geçmelidir.
"Orta etki" bir kategoridir; kullanıcı onaylamadan 0.5 araca gitmez. Bu bir hesap değil, metin denetimidir.
"""

import math
import re
from typing import Any, Dict, Iterable, List, Set

NUMERIC_FIELDS = ("dz", "f2", "alpha", "power", "n_total", "predictors", "beta_alpha_ratio")

NUMBER = re.compile(r"(?<![\w.,])(%\s*)?(\d+(?:[.,]\d+)?|[.,]\d+)(\s*%)?")
ONE_TAILED = re.compile(r"tek\s*(yönlü|yonlu|kuyruk|taraflı|tarafli)|one[\s-]*(tailed|sided)|tails?\s*[:=]?\s*1\b")
TWO_TAILED = re.compile(r"(çift|cift|iki)\s*(yönlü|yonlu|kuyruk|taraflı|tarafli)|two[\s-]*(tailed|sided)"
                        r"|tails?\s*[:=]?\s*2\b")
AFFIRMATIVE = re.compile(r"^\s*(evet|onay|onaylıyorum|olur|tamam|kabul|uygun|doğru|yes|ok|okay)\b")


def stated_numbers(text: str) -> Set[float]:
    numbers = set()
    for match in NUMBER.finditer(text):
        value = float(match.group(2).replace(",", "."))
        numbers.add(value)
        if match.group(1) or match.group(3):  # %5 ya da 95%
            numbers.add(value / 100.0)
    return numbers


def stated_tails(text: str) -> Set[int]:
    lowered = text.casefold()
    tails = set()
    if ONE_TAILED.search(lowered):
        tails.add(1)
    if TWO_TAILED.search(lowered):
        tails.add(2)
    return tails


def is_affirmative(text: str) -> bool:
    return bool(AFFIRMATIVE.match(text.casefold()))


def ungrounded_fields(arguments: Dict[str, Any], sources: Iterable[str]) -> List[str]:
    """Kaynak metinlerde geçmeyen alanların adları (araç şemasındaki sırayla)."""
    sources = list(sources)
    numbers = set().union(*(stated_numbers(s) for s in sources)) if sources else set()
    tails = set().union(*(stated_tails(s) for s in sources)) if sources else set()

    missing = []
    for key, value in arguments.items():
        if key == "tails":
            if value not in tails:
                missing.append(key)
        elif key in NUMERIC_FIELDS:
            try:
                number = float(value)
            except (TypeError, ValueError):
                continue  # biçim hatasını motor bildirir
            if not any(math.isclose(number, n, rel_tol=1e-9, abs_tol=1e-12) for n in numbers):
                missing.append(key)
    return missing
