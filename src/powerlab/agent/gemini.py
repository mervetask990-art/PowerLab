"""
src/powerlab/agent/gemini.py
Gemini API istemcisi (REST, generateContent, function calling). Ek paket gerektirmez: yalnızca urllib.

Anahtar URL'ye değil x-goog-api-key başlığına konur; hata mesajlarına ve loga yazılmaz.
Modelin döndürdüğü içerik geçmişe aynen eklenir (thoughtSignature gibi alanlar korunur).
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

API_ROOT = "https://generativelanguage.googleapis.com/v1beta"


class ModelError(Exception):
    pass


@dataclass(frozen=True)
class FunctionCall:
    name: str
    args: Dict[str, Any]


@dataclass
class ModelReply:
    text: str
    calls: List[FunctionCall]
    tokens_in: int
    tokens_out: int
    # Geçmişe eklenecek model sırası (Gemini "content"); None ise ajan metin ve çağrılardan kurar.
    content: Optional[Dict[str, Any]]


def _gemini_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Gemini'nin şema alt kümesi: enum yalnızca string tiplerde geçerlidir."""
    out = {}
    for key, value in schema.items():
        if key == "enum" and schema.get("type") != "string":
            continue
        if key == "properties":
            value = {name: _gemini_schema(prop) for name, prop in value.items()}
        out[key] = value
    return out


def to_declaration(tool: Dict[str, Any]) -> Dict[str, Any]:
    return {"name": tool["name"], "description": tool["description"],
            "parameters": _gemini_schema(tool["inputSchema"])}


# Ücretsiz katmanın hız sınırı (429) ve geçici sunucu hataları için bekleme süreleri (saniye).
RETRY_STATUS = {429, 500, 503}
RETRY_DELAYS = (5.0, 15.0, 30.0)


class GeminiModel:
    def __init__(self, api_key: str, model: str, timeout: float = 60.0,
                 opener: Callable = urllib.request.urlopen, sleep: Callable = time.sleep):
        self._api_key = api_key
        self.model = model
        self.timeout = timeout
        self._opener = opener
        self._sleep = sleep

    def __repr__(self) -> str:
        return f"GeminiModel(model={self.model!r})"

    def generate(self, system: str, contents: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> ModelReply:
        body = {"systemInstruction": {"parts": [{"text": system}]}, "contents": contents}
        if tools:
            body["tools"] = [{"functionDeclarations": [to_declaration(t) for t in tools]}]
        return _parse(self._post(body))

    def generate_json(self, system: str, text: str, schema: Dict[str, Any]) -> ModelReply:
        """Yanıtı şemaya kısıtlı JSON olarak ister (etiket sınıflandırması); ModelReply.text JSON metnidir."""
        body = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": text}]}],
            "generationConfig": {"responseMimeType": "application/json", "responseSchema": schema},
        }
        return _parse(self._post(body))

    def _post(self, body: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{API_ROOT}/models/{urllib.parse.quote(self.model, safe='-._')}:generateContent"
        payload = json.dumps(body).encode("utf-8")
        for attempt in range(len(RETRY_DELAYS) + 1):
            request = urllib.request.Request(url, data=payload, method="POST",
                                             headers={"Content-Type": "application/json",
                                                      "x-goog-api-key": self._api_key})
            try:
                with self._opener(request, timeout=self.timeout) as response:
                    return json.loads(response.read())
            except urllib.error.HTTPError as err:
                if err.code in RETRY_STATUS and attempt < len(RETRY_DELAYS):
                    self._sleep(RETRY_DELAYS[attempt])
                    continue
                raise ModelError(f"Gemini HTTP {err.code}: {_error_message(err)}") from None
            except urllib.error.URLError as err:
                raise ModelError(f"Gemini'ye bağlanılamadı: {err.reason}") from None
        raise AssertionError("ulaşılamaz")


def _error_message(err: urllib.error.HTTPError) -> str:
    try:
        return json.loads(err.read())["error"]["message"]
    except (ValueError, KeyError, TypeError, OSError):
        return err.reason


def _parse(data: Dict[str, Any]) -> ModelReply:
    candidates = data.get("candidates") or []
    if not candidates:
        reason = (data.get("promptFeedback") or {}).get("blockReason", "bilinmiyor")
        raise ModelError(f"Gemini yanıt üretmedi (neden: {reason})")
    content = candidates[0].get("content") or {"role": "model", "parts": []}
    content.setdefault("role", "model")
    texts, calls = [], []
    for part in content.get("parts", []):
        if "functionCall" in part:
            call = part["functionCall"]
            calls.append(FunctionCall(call["name"], call.get("args") or {}))
        elif "text" in part and not part.get("thought"):
            texts.append(part["text"])
    usage = data.get("usageMetadata") or {}
    return ModelReply(text="".join(texts).strip(), calls=calls,
                      tokens_in=int(usage.get("promptTokenCount", 0)),
                      tokens_out=int(usage.get("candidatesTokenCount", 0)) + int(usage.get("thoughtsTokenCount", 0)),
                      content=content)
