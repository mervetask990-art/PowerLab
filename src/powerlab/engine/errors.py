"""
src/powerlab/engine/errors.py
Sözleşme hata türü: CONTRACT.md §2.4'teki `code` ve `field` bilgisini taşıyan ValueError.
"""

from typing import Optional

MISSING_PARAM = "MISSING_PARAM"
UNKNOWN_PARAM = "UNKNOWN_PARAM"
INVALID_VALUE = "INVALID_VALUE"
OUT_OF_RANGE = "OUT_OF_RANGE"
INCONSISTENT = "INCONSISTENT"
UNSUPPORTED = "UNSUPPORTED"
NO_SOLUTION = "NO_SOLUTION"


class ContractError(ValueError):
    """Geçersiz girdi: CLI çıkış kodu 2, JSON {"error", "code", "field"}."""

    def __init__(self, code: str, field: Optional[str], message: str):
        super().__init__(message)
        self.code = code
        self.field = field
