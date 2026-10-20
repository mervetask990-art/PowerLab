"""
src/powerlab/cli.py
İnce katman CLI arayüzü: argparse -> engine -> tek satır JSON.
Hesap mantığı içermez, yalnızca engine katmanını çağırır.

Çıktı sözleşmesi: başarı ve hata dahil her sonuç STDOUT'a tek satır JSON olarak yazılır;
hata durumunda {"error": "..."} ve sıfırdan farklı çıkış kodu (1: hesap/doğrulama, 2: argüman).
stderr'e hiçbir şey yazılmaz. --help normal metin yazar ve 0 ile çıkar.
"""

import argparse
import json
import sys
from typing import List, Optional

from powerlab.engine.solver import run_power_analysis

EXIT_ENGINE_ERROR = 1
EXIT_USAGE_ERROR = 2


def _emit(payload: dict) -> None:
    print(json.dumps(payload, separators=(",", ":")))


class JsonArgumentParser(argparse.ArgumentParser):
    """Argüman hatalarını (bilinmeyen/eksik parametre, geçersiz seçenek) JSON olarak bildirir."""

    def error(self, message: str) -> None:
        _emit({"error": f"Geçersiz argüman: {message}"})
        sys.exit(EXIT_USAGE_ERROR)


def build_parser() -> argparse.ArgumentParser:
    parser = JsonArgumentParser(
        prog="gpower-clone",
        description="powerlab: G*Power Uyumlu Güç Analizi ve Boyut Belirleme Motoru",
    )
    parser.add_argument("--test", type=str, required=True, help="Test ailesi (örn: t-paired)")
    parser.add_argument(
        "--mode",
        type=str,
        default="a-priori",
        choices=["a-priori", "post-hoc", "a_priori", "post_hoc"],
        help="Analiz modu: a-priori veya post-hoc",
    )
    parser.add_argument("--tails", type=int, default=2, choices=[1, 2], help="Kuyruk sayısı (1 veya 2)")
    parser.add_argument("--dz", type=float, default=None, help="Eşleştirilmiş t-testi etki büyüklüğü (dz)")
    parser.add_argument("--d", type=float, default=None, help="Genel etki büyüklüğü d (dz yerine kullanılabilir)")
    parser.add_argument("--alpha", type=float, required=True, help="Tip I hata oranı (alpha, örn: 0.05)")
    parser.add_argument("--power", type=float, default=None, help="Hedef güç (1 - beta, örn: 0.95)")
    parser.add_argument("--n", type=int, default=None, help="Örneklem büyüklüğü (post-hoc için çift sayısı)")
    parser.add_argument("--ratio", type=float, default=1.0, help="Grup oranı n2/n1 (bağımsız testler için)")
    return parser


def _force_utf8_streams() -> None:
    """Windows konsolunda Türkçe karakterler (--help metni vb.) bozulmasın."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


def main(args: Optional[List[str]] = None) -> None:
    _force_utf8_streams()
    parser = build_parser()
    parsed = parser.parse_args(args)

    params = {}
    # dz veya d desteği
    dz_val = parsed.dz if parsed.dz is not None else parsed.d
    if dz_val is not None:
        params["dz"] = dz_val
    params["tails"] = parsed.tails
    params["alpha"] = parsed.alpha
    if parsed.power is not None:
        params["power"] = parsed.power
    if parsed.n is not None:
        params["n"] = parsed.n
    if parsed.ratio is not None:
        params["ratio"] = parsed.ratio

    try:
        result = run_power_analysis(test=parsed.test, mode=parsed.mode, params=params)
    except Exception as err:
        _emit({"error": str(err)})
        sys.exit(EXIT_ENGINE_ERROR)
    _emit(result)
    sys.exit(0)


if __name__ == "__main__":
    main()
