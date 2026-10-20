"""
src/powerlab/cli.py
İnce katman CLI arayüzü: argparse -> engine -> tek satır JSON.
Hesap mantığı içermez, yalnızca engine katmanını çağırır.
"""

import argparse
import json
import sys
from typing import List, Optional

from powerlab.engine.solver import run_power_analysis


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="powerlab",
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


def main(args: Optional[List[str]] = None) -> None:
    parser = build_parser()
    try:
        parsed = parser.parse_args(args)
    except SystemExit as e:
        # argparse default çıkışlarında sıfırdan farklı exit code korunsun
        sys.exit(e.code)

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
        # Tek satır saf JSON çıktısı (Ödev sözleşmesi)
        print(json.dumps(result, separators=(",", ":")))
        sys.exit(0)
    except Exception as err:
        # Hata durumunda JSON formatında açıklama ve exit code != 0
        error_payload = {"error": str(err)}
        print(json.dumps(error_payload, separators=(",", ":")), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
