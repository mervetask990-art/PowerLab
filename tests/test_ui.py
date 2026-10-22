"""
tests/test_ui.py
İsteğe bağlı yerel web arayüzü (gpower-clone-ui; ödev kapsamı dışında).
Arayüz hesap yapmaz: her istek powerlab.engine.contract.handle_request'e gider ve yanıttaki
"sonuc", aynı girdide handle_request'in verdiğiyle birebir aynıdır. Sunucu yalnızca 127.0.0.1'i
dinler ve yabancı Host başlıklarını reddeder.
"""

import json
import threading
import urllib.error
import urllib.request

import pytest

from powerlab.engine.contract import handle_request
from powerlab.ui import server as ui

APRIORI = {"mode": "a-priori", "tails": "2", "dz": "0.5", "alpha": "0.05", "power": "0.95"}
POSTHOC = {"mode": "post-hoc", "tails": "2", "dz": "0.5", "alpha": "0.05", "n_total": "30"}


@pytest.fixture(scope="module")
def base_url():
    httpd = ui.make_server(port=0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()
    httpd.server_close()


def _request(url, data=None, headers=None, method=None):
    body = None if data is None else json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    if body is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, resp.headers, resp.read().decode("utf-8")
    except urllib.error.HTTPError as err:
        return err.code, err.headers, err.read().decode("utf-8")


def _calc(base_url, data):
    status, _, text = _request(base_url + "/api/hesapla", data)
    return status, json.loads(text)


def test_page_is_turkish_with_two_tabs_and_clinical_help(base_url):
    status, headers, html = _request(base_url + "/")
    assert status == 200
    assert headers["Content-Type"].startswith("text/html")
    for text in ("Kaç katılımcıya ihtiyacım var?", "Çalışmamın gücü ne?",
                 "Tek yönlü", "Çift yönlü", "Gerçekte fark yokken", "Gerçekte fark varken",
                 "0.2", "0.5", "0.8", "G*Power değildir"):
        assert text in html, text


def test_page_has_no_external_resources(base_url):
    _, headers, html = _request(base_url + "/")
    assert "http://" not in html.replace("http://www.w3.org", "")
    assert "https://" not in html
    assert "default-src 'none'" in headers["Content-Security-Policy"]


@pytest.mark.parametrize("data", [APRIORI, POSTHOC], ids=["a-priori", "post-hoc"])
def test_result_equals_handle_request(base_url, data):
    status, body = _calc(base_url, data)
    expected, code = handle_request({"test": "t-paired", **data})
    assert status == 200
    assert body["ok"] is True
    assert body["sonuc"] == expected
    assert body["cikis_kodu"] == code == 0


@pytest.mark.parametrize(
    "data, code, field, fragment",
    [
        ({**APRIORI, "dz": "0"}, "OUT_OF_RANGE", "dz", "0'dan büyük"),
        ({**APRIORI, "power": "0.03"}, "INCONSISTENT", "power", "α'dan küçük olamaz"),
        ({**POSTHOC, "n_total": "2"}, "OUT_OF_RANGE", "n_total", "En az 3 çift"),
        ({k: v for k, v in APRIORI.items() if k != "tails"}, "MISSING_PARAM", "tails", "yönünü seçin"),
        ({**APRIORI, "alpha": "abc"}, "INVALID_VALUE", "alpha", "geçerli bir sayı"),
    ],
    ids=["dz-sifir", "guc-alfadan-kucuk", "posthoc-n2", "yon-eksik", "alfa-metin"],
)
def test_errors_have_contract_code_and_plain_turkish_message(base_url, data, code, field, fragment):
    status, body = _calc(base_url, data)
    assert status == 200
    assert body["ok"] is False
    assert (body["sonuc"]["code"], body["sonuc"]["field"]) == (code, field)
    assert fragment in body["mesaj"]


@pytest.mark.parametrize("extra", [{"test": "anova-oneway"}, {"mode": "compromise"}], ids=["test", "mod"])
def test_only_t_paired_and_two_modes(base_url, extra):
    status, body = _calc(base_url, {**APRIORI, **extra})
    assert status == 400
    assert body["ok"] is False
    assert "yalnızca" in body["mesaj"]


def test_binds_only_to_loopback():
    httpd = ui.make_server(port=0)
    try:
        assert httpd.server_address[0] == "127.0.0.1"
    finally:
        httpd.server_close()


def test_foreign_host_header_is_rejected(base_url):
    status, _, _ = _request(base_url + "/", headers={"Host": "evil.example:80"})
    assert status == 403
    status, _, _ = _request(base_url + "/api/hesapla", APRIORI, headers={"Host": "evil.example"})
    assert status == 403


def test_unknown_path_and_wrong_requests(base_url):
    assert _request(base_url + "/yok")[0] == 404
    assert _request(base_url + "/api/hesapla")[0] == 405  # GET yerine POST beklenir
    req = urllib.request.Request(base_url + "/api/hesapla", data=b"x=1", method="POST",
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with pytest.raises(urllib.error.HTTPError) as exc:
        urllib.request.urlopen(req, timeout=10)
    assert exc.value.code == 415
