"""
src/powerlab/cli.py
İnce katman CLI (CONTRACT.md §2): argv -> alan sözlüğü -> powerlab.engine.contract -> tek satır JSON.
Hesap ve alan doğrulaması içermez; alan adları birebir, takma ad ve varsayılan değer yoktur.

Başarıda çıkış kodu 0; geçersiz girdide {"error","code","field"} ve 2; iç hatada 1.
stderr'e hiçbir şey yazılmaz. --help normal metin yazar ve 0 ile çıkar; --version JSON yazar.
"""

import sys
from typing import Dict, List, Optional

from powerlab.engine.contract import EXIT_INVALID_INPUT, EXIT_OK, dumps, error_payload, handle_request, version_payload
from powerlab.engine.errors import INVALID_VALUE, UNKNOWN_PARAM, ContractError

HELP = """usage: gpower-clone --test <TEST_ID> --mode <MODE_ID> [--<alan> <değer> ...]
       gpower-clone --version

powerlab: G*Power 3.1.9.7 davranışını referans alan bağımsız bir yeniden yazım; G*Power değildir.
Arayüz: CONTRACT.md 1.0.0. Varsayılan değer yoktur; alan adları birebirdir.

t-paired:
  --mode a-priori   --tails <1|2> --dz <etki> --alpha <α> --power <1-β>
  --mode post-hoc   --tails <1|2> --dz <etki> --alpha <α> --n_total <çift sayısı>

Alanlar:
  --tails     Kuyruk sayısı: 1 (tek yönlü) ya da 2 (çift yönlü)
  --dz        Etki büyüklüğü dz (> 0)
  --alpha     I. tip hata olasılığı (0 < α < 1)
  --power     Hedef güç, 1-β (0 < güç < 1, güç >= α)
  --n_total   Toplam örneklem büyüklüğü, çift sayısı (post hoc'ta >= 3)

Değer '=' ile de verilebilir: --dz=0.5
"""


def _emit(payload: dict) -> None:
    print(dumps(payload))


def parse_argv(argv: List[str]) -> Dict[str, str]:
    """`--alan değer` ve `--alan=değer` biçimlerini alan sözlüğüne çevirir; değerleri yorumlamaz."""
    fields: Dict[str, str] = {}
    i = 0
    while i < len(argv):
        token = argv[i]
        if not token.startswith("--") or token == "--":
            raise ContractError(UNKNOWN_PARAM, token, f"Tanınmayan argüman: '{token}'")
        name, has_value, value = token[2:].partition("=")
        if has_value:
            i += 1
        elif i + 1 < len(argv) and not argv[i + 1].startswith("--"):
            value = argv[i + 1]
            i += 2
        else:
            raise ContractError(INVALID_VALUE, name, f"--{name} için değer verilmedi")
        if name in fields:
            raise ContractError(INVALID_VALUE, name, f"--{name} birden çok kez verildi")
        fields[name] = value
    return fields


def _force_utf8_streams() -> None:
    """Windows konsolunda Türkçe karakterler (--help metni vb.) bozulmasın."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError, OSError):
            pass


def main(args: Optional[List[str]] = None) -> None:
    _force_utf8_streams()
    argv = sys.argv[1:] if args is None else list(args)

    if "--help" in argv or "-h" in argv:
        print(HELP, end="")
        sys.exit(EXIT_OK)
    if argv == ["--version"]:
        _emit(version_payload())
        sys.exit(EXIT_OK)

    try:
        fields = parse_argv(argv)
    except ContractError as err:
        _emit(error_payload(err.code, err.field, str(err)))
        sys.exit(EXIT_INVALID_INPUT)

    payload, exit_code = handle_request(fields)
    _emit(payload)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
