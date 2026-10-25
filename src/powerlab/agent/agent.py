"""
src/powerlab/agent/agent.py
CONTRACT.md §8 AI ajanı: soruyu modele verir, model power_analysis MCP aracını çağırır; ajan hiçbir sayıyı
hesaplamaz. Araca ulaşan her çağrı logs/agent_calls.jsonl dosyasına tek satır yazılır:
{"ts", "question", "tool_input", "tool_output", "tokens_in", "tokens_out"}.

§10: Kullanıcının söylemediği bir değer (ör. yalnızca "orta etki" dendiğinde dz = 0.5) araca gitmez;
grounding.ungrounded_fields çağrıyı durdurur ve modele NOT_STATED döner, model kullanıcıya sorar.
tokens_in / tokens_out, çağrıyı üreten model yanıtının token sayılarıdır (aynı yanıttaki ikinci ve sonraki
çağrılarda 0).
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from powerlab.agent.grounding import is_affirmative, ungrounded_fields
from powerlab.engine.contract import INTEGER_FIELDS
from powerlab.mcp_server import TOOL_NAME

DEFAULT_LOG = Path("logs") / "agent_calls.jsonl"
MAX_STEPS = 6

SYSTEM_PROMPT = """\
Sen istatistiksel güç analizi için bir araştırma asistanısın. Kurallar:
1. Hiçbir sayıyı kendin hesaplama ya da tahmin etme. Tüm sonuçlar power_analysis aracından gelir; aracın
   döndürdüğü değerleri değiştirmeden aktar.
2. Desteklenen testler: t-paired (aynı deneklerde iki ölçüm, önce-sonra, eşleştirilmiş çiftler) ve
   multireg-r2 (çoklu doğrusal regresyon, R² sıfırdan sapma). Başka bir test istenirse (bağımsız iki grup,
   ANOVA, ki-kare, Wilcoxon, sağkalım...) hesap yapma; bu ajanın kapsamı dışında olduğunu söyle.
3. Kullanıcının açıkça yazmadığı hiçbir değeri (dz, f2, alpha, power, n_total, predictors,
   beta_alpha_ratio) ve kuyruk sayısını (tails: tek yönlü 1, çift yönlü 2) varsayma.
   "Küçük / orta / büyük etki" bir kategoridir, değer değildir: Cohen'in geleneksel değerini öner
   (t-paired dz: 0.2 / 0.5 / 0.8; multireg f2: 0.02 / 0.15 / 0.35) ve kullanmadan önce kullanıcıdan onay iste.
4. Eksik değer varsa aracı çağırmadan önce kullanıcıya sor; bütün eksikleri tek mesajda sor.
5. Mod seçimi: örneklem büyüklüğü isteniyorsa a-priori; N verilip güç isteniyorsa post-hoc;
   β/α oranı verilmişse compromise; N ve güç verilip α isteniyorsa criterion; N, α ve güç verilip
   saptanabilir en küçük etki isteniyorsa sensitivity.
6. Araç NOT_STATED dönerse belirtilen alanları kullanıcıya sor. Araç başka bir hata dönerse hatayı
   açıkla; değeri kendin değiştirip yeniden deneme.
7. Yanıtı Türkçe ve kısa ver; aracın döndürdüğü temel değerleri (ör. n_total, actual_power, power) yaz.
"""


class Agent:
    def __init__(self, model, tools, log_path: Path = DEFAULT_LOG, max_steps: int = MAX_STEPS):
        self.model = model
        self.tools = tools
        self.log_path = Path(log_path)
        self.max_steps = max_steps
        self.history: List[Dict[str, Any]] = []
        self.user_messages: List[str] = []
        self.grounding_sources: List[str] = []
        self._last_answer = ""
        self._declarations = tools.list_tools()

    def ask(self, message: str) -> str:
        """Bir kullanıcı mesajını işler; modelin son metin yanıtını döndürür."""
        self.user_messages.append(message)
        self.grounding_sources.append(message)
        if self._last_answer and is_affirmative(message):
            # Kullanıcı ajanın önerisini onayladı (ör. "dz = 0.5 kullanayım mı?" -> "evet").
            self.grounding_sources.append(self._last_answer)
        self.history.append({"role": "user", "parts": [{"text": message}]})

        for _ in range(self.max_steps):
            reply = self.model.generate(SYSTEM_PROMPT, self.history, self._declarations)
            self.history.append(reply.content or _content_from(reply))
            if not reply.calls:
                self._last_answer = reply.text
                return reply.text

            responses = []
            tokens = (reply.tokens_in, reply.tokens_out)
            for call in reply.calls:
                output = self._run(call.name, call.args, tokens)
                if output.get("code") != "NOT_STATED" and call.name == TOOL_NAME:
                    tokens = (0, 0)
                responses.append({"functionResponse": {"name": call.name, "response": output}})
            self.history.append({"role": "user", "parts": responses})

        self._last_answer = ""
        return f"Ajan {self.max_steps} adımda yanıt üretemedi; soruyu daha açık yazıp yeniden deneyin."

    def _run(self, name: str, args: Dict[str, Any], tokens) -> Dict[str, Any]:
        if name != TOOL_NAME:
            return {"error": f"Bilinmeyen araç: '{name}'. Yalnızca {TOOL_NAME} kullanılabilir.",
                    "code": "UNKNOWN_TOOL", "field": None}
        arguments = _normalize(args)
        missing = ungrounded_fields(arguments, self.grounding_sources)
        if missing:
            return {"error": "Bu değerleri kullanıcı yazmadı ya da onaylamadı; varsayma, kullanıcıya sor.",
                    "code": "NOT_STATED", "fields": missing}
        output = self.tools.call(arguments)
        self._log(arguments, output, tokens)
        return output

    def _log(self, tool_input, tool_output, tokens) -> None:
        line = {
            "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
            "question": " | ".join(self.user_messages),
            "tool_input": tool_input,
            "tool_output": tool_output,
            "tokens_in": tokens[0],
            "tokens_out": tokens[1],
        }
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(line, ensure_ascii=False) + "\n")


def _normalize(args: Dict[str, Any]) -> Dict[str, Any]:
    """Model tamsayı alanlarını 45.0 gibi gönderebilir; tür dönüşümüdür, hesap değildir."""
    out = {}
    for key, value in args.items():
        if key in INTEGER_FIELDS and isinstance(value, float) and value.is_integer():
            value = int(value)
        out[key] = value
    return out


def _content_from(reply) -> Dict[str, Any]:
    parts = [{"text": reply.text}] if reply.text else []
    parts += [{"functionCall": {"name": c.name, "args": c.args}} for c in reply.calls]
    return {"role": "model", "parts": parts}


EXIT_WORDS = {"çıkış", "cikis", "q", "quit", "exit"}


def main(argv: Optional[List[str]] = None) -> int:
    """gpower-clone-agent: Türkçe soru-cevap; ajan sorarsa yanıt yazılır, 'çıkış' ile biter."""
    from powerlab.agent.config import ConfigError, load_settings
    from powerlab.agent.gemini import GeminiModel, ModelError
    from powerlab.agent.mcp_client import MCPClient, MCPError

    parser = argparse.ArgumentParser(prog="gpower-clone-agent", description="Güç analizi ajanı (Gemini + MCP)")
    parser.add_argument("--question", help="İlk soru; verilmezse sorulur")
    parser.add_argument("--reply", action="append", default=[],
                        help="Ajan soru sorarsa sırayla verilecek yanıtlar (etkileşimsiz demo için)")
    parser.add_argument("--once", action="store_true", help="Verilen soru ve yanıtlardan sonra çık")
    parser.add_argument("--log", default=str(DEFAULT_LOG), help="Log dosyası (varsayılan logs/agent_calls.jsonl)")
    args = parser.parse_args(argv)

    try:
        settings = load_settings()
    except ConfigError as err:
        print(err)
        return 2

    pending = ([args.question] if args.question else []) + args.reply
    print(f"Güç analizi ajanı (model: {settings.model}). Çıkmak için 'çıkış' yazın.")
    try:
        with MCPClient() as tools:
            agent = Agent(GeminiModel(settings.api_key, settings.model), tools, Path(args.log))
            while True:
                if pending:
                    message = pending.pop(0)
                    print(f"\nSiz: {message}")
                elif args.once:
                    return 0
                else:
                    try:
                        message = input("\nSiz: ").strip()
                    except EOFError:
                        return 0
                if not message:
                    continue
                if message.casefold() in EXIT_WORDS:
                    return 0
                print(f"\nAjan: {agent.ask(message)}")
    except (ModelError, MCPError) as err:
        print(f"\nHata: {err}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
