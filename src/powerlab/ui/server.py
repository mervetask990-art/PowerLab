"""
src/powerlab/ui/server.py
İsteğe bağlı yerel web arayüzü (ödev kapsamı dışında): `gpower-clone-ui`.

İnce katmandır: hesap yapmaz. Her istek powerlab.engine.contract.handle_request'e gider; yanıttaki
"sonuc" CLI'ın aynı girdide yazdığı JSON ile aynıdır. Bu modül yalnızca hata kodlarını sade
Türkçeye çevirir. Yalnızca 127.0.0.1'i dinler; yabancı Host başlıklarını reddeder (DNS rebinding).
Yalnızca Python standart kütüphanesini kullanır.
"""

import argparse
import json
import sys
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources
from typing import Any, Dict, Optional, Tuple

from powerlab.engine.contract import handle_request

HOST = "127.0.0.1"
TEST_ID = "t-paired"
MODES = ("a-priori", "post-hoc")
MAX_BODY_BYTES = 10_000

SECURITY_HEADERS = {
    "Content-Security-Policy": (
        "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; "
        "connect-src 'self'; img-src data:; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
    ),
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "Cache-Control": "no-store",
}

LABELS = {
    "tails": "Hipotezin yönü",
    "dz": "Etki büyüklüğü (dz)",
    "alpha": "Yanılma payı (α)",
    "power": "İstenen güç",
    "n_total": "Çift sayısı",
}

ONLY_SUPPORTED = "Bu arayüz yalnızca eşleştirilmiş örneklem (önce–sonra) hesabının iki modunu destekler."


def friendly_message(payload: Dict[str, Any], mode: str) -> str:
    """Sözleşme hata kodunu (CONTRACT.md §2.4) teknik olmayan bir kullanıcıya anlatır."""
    code, field = payload.get("code"), payload.get("field")
    label = LABELS.get(field, field)
    if code == "MISSING_PARAM":
        if field == "tails":
            return "Lütfen hipotezinizin yönünü seçin (tek yönlü ya da çift yönlü)."
        return f"Lütfen “{label}” alanını doldurun."
    if code == "INVALID_VALUE":
        if field == "n_total":
            return "Çift sayısı için tam sayı girin (örneğin 30)."
        return f"“{label}” için geçerli bir sayı girin (örneğin 0.05)."
    if code == "OUT_OF_RANGE":
        if field == "dz":
            if mode == "post-hoc":
                return "Etki büyüklüğü 0'dan büyük olmalı ve 20'yi geçmemeli."
            return "Etki büyüklüğü 0'dan büyük olmalı (en az 0.00001)."
        if field == "n_total":
            return "En az 3 çift gerekir."
        if field in ("alpha", "power"):
            return f"“{label}” 0 ile 1 arasında olmalı (örneğin {'0.05' if field == 'alpha' else '0.80'})."
        if field == "tails":
            return "Hipotezin yönü tek yönlü ya da çift yönlü olmalı."
    if code == "INCONSISTENT" and field == "power":
        return "Güç, α'dan küçük olamaz. Gücü en az α kadar yapın (genellikle 0.80 ve üzeri)."
    if code in ("UNSUPPORTED", "UNKNOWN_PARAM"):
        return ONLY_SUPPORTED
    return payload.get("error") or "Beklenmeyen bir hata oluştu."


def calculate(data: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    """Arayüz isteğini işler: (HTTP durum kodu, yanıt gövdesi)."""
    test = data.pop("test", TEST_ID)
    mode = data.get("mode")
    if test != TEST_ID or mode not in MODES:
        return HTTPStatus.BAD_REQUEST, {"ok": False, "sonuc": None, "cikis_kodu": 2, "mesaj": ONLY_SUPPORTED}

    payload, exit_code = handle_request({"test": TEST_ID, **data})
    body = {"ok": exit_code == 0, "sonuc": payload, "cikis_kodu": exit_code, "mesaj": None}
    if exit_code != 0:
        body["mesaj"] = friendly_message(payload, mode)
    return HTTPStatus.OK, body


def _load_page() -> bytes:
    return resources.files("powerlab.ui").joinpath("index.html").read_bytes()


class Handler(BaseHTTPRequestHandler):
    server_version = "powerlab-ui"
    sys_version = ""

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002 - BaseHTTPRequestHandler imzası
        pass  # İstek günlüğü yazılmaz.

    def _host_allowed(self) -> bool:
        port = self.server.server_address[1]
        return self.headers.get("Host", "") in (f"{HOST}:{port}", f"localhost:{port}")

    def _send(self, status: int, content_type: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        for name, value in SECURITY_HEADERS.items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status: int, data: Dict[str, Any]) -> None:
        self._send(status, "application/json; charset=utf-8", json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _send_text(self, status: int, text: str) -> None:
        self._send(status, "text/plain; charset=utf-8", text.encode("utf-8"))

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler adı
        if not self._host_allowed():
            return self._send_text(HTTPStatus.FORBIDDEN, "Yalnızca yerel erişim.")
        if self.path in ("/", "/index.html"):
            return self._send(HTTPStatus.OK, "text/html; charset=utf-8", _load_page())
        if self.path == "/api/hesapla":
            return self._send_text(HTTPStatus.METHOD_NOT_ALLOWED, "Bu adres yalnızca POST kabul eder.")
        return self._send_text(HTTPStatus.NOT_FOUND, "Sayfa bulunamadı.")

    def do_POST(self) -> None:  # noqa: N802
        if not self._host_allowed():
            return self._send_text(HTTPStatus.FORBIDDEN, "Yalnızca yerel erişim.")
        if self.path != "/api/hesapla":
            return self._send_text(HTTPStatus.NOT_FOUND, "Sayfa bulunamadı.")
        if not self.headers.get("Content-Type", "").startswith("application/json"):
            return self._send_text(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "JSON bekleniyor.")
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = -1
        if not 0 < length <= MAX_BODY_BYTES:
            return self._send_text(HTTPStatus.BAD_REQUEST, "Geçersiz istek boyutu.")
        try:
            data = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return self._send_text(HTTPStatus.BAD_REQUEST, "Geçersiz JSON.")
        if not isinstance(data, dict):
            return self._send_text(HTTPStatus.BAD_REQUEST, "Geçersiz JSON.")
        status, body = calculate(data)
        self._send_json(status, body)


def make_server(port: int = 0) -> ThreadingHTTPServer:
    """Yalnızca 127.0.0.1'e bağlı bir sunucu döner; port 0 ise boş bir port seçilir."""
    return ThreadingHTTPServer((HOST, port), Handler)


def main(args: Optional[list] = None) -> None:
    parser = argparse.ArgumentParser(
        prog="gpower-clone-ui",
        description="Eşleştirilmiş örneklem güç hesabı için yerel web arayüzü (isteğe bağlı ek).",
    )
    parser.add_argument("--port", type=int, default=0, help="Dinlenecek port (varsayılan: boş bir port)")
    parser.add_argument("--no-browser", action="store_true", help="Tarayıcıyı otomatik açma")
    parsed = parser.parse_args(args)
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError, OSError):
            pass

    httpd = make_server(parsed.port)
    url = f"http://{HOST}:{httpd.server_address[1]}/"
    print(f"Arayüz çalışıyor: {url}  (kapatmak için Ctrl+C)", flush=True)
    if not parsed.no_browser:
        threading.Timer(0.5, webbrowser.open, args=(url,)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        print("Arayüz kapatıldı.", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
