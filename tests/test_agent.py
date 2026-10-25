"""
tests/test_agent.py
CONTRACT.md §8 ajanı: ajan MCP aracını çağırır, hesabı asla kendisi yapmaz; her araç çağrısı
logs/agent_calls.jsonl dosyasına tek satır yazılır. §10: "orta etki" bir kategoridir; ajan değeri
sessizce varsaymaz. Testler gerçek model kullanmaz (sahte model); Gemini istemcisi ağsız sınanır.
"""

import io
import json
import re
import subprocess
from pathlib import Path

import pytest

from powerlab.agent.agent import Agent
from powerlab.agent.config import ConfigError, load_settings
from powerlab.agent.gemini import FunctionCall, GeminiModel, ModelReply, to_declaration
from powerlab.agent.grounding import stated_numbers, ungrounded_fields
from powerlab.agent.mcp_client import MCPClient
from powerlab.mcp_server import POWER_ANALYSIS_TOOL_SCHEMA, call_tool

REPO = Path(__file__).parent.parent
LOG_FIELDS = ["ts", "question", "tool_input", "tool_output", "tokens_in", "tokens_out"]
PAIRED = {"test": "t-paired", "mode": "a-priori", "tails": 1, "dz": 0.5, "alpha": 0.05, "power": 0.95}
# Gerçek anahtar biçimine (AIza + 35 karakter) uymaz; aşağıdaki repo taraması kendini yakalamasın.
FAKE_KEY = "AIza.TEST.not.a.real.key"


class FakeModel:
    """Senaryodaki yanıtları sırayla döndürür; aldığı geçmişi kaydeder."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.seen = []

    def generate(self, system, contents, tools):
        self.seen.append(json.loads(json.dumps(contents)))
        return self.replies.pop(0)


class RecordingTools:
    """MCP istemcisi yerine geçer; çağrıları kaydeder, sonucu motordan alır."""

    def __init__(self):
        self.calls = []

    def list_tools(self):
        return [POWER_ANALYSIS_TOOL_SCHEMA]

    def call(self, arguments):
        self.calls.append(arguments)
        return call_tool("power_analysis", arguments)


def call_reply(args, tokens_in=100, tokens_out=20):
    return ModelReply(text="", calls=[FunctionCall("power_analysis", args)],
                      tokens_in=tokens_in, tokens_out=tokens_out, content=None)


def text_reply(text, tokens_in=150, tokens_out=30):
    return ModelReply(text=text, calls=[], tokens_in=tokens_in, tokens_out=tokens_out, content=None)


def read_log(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


# --- Ajan döngüsü ------------------------------------------------------------------------------

def test_explicit_question_calls_real_mcp_server_and_logs(tmp_path):
    log = tmp_path / "logs" / "agent_calls.jsonl"
    question = "Önce-sonra ölçümlü kurgusal bir çalışma: tek yönlü, dz 0.5, alpha 0.05, güç 0.95. Kaç çift gerekir?"
    model = FakeModel([call_reply(PAIRED), text_reply("45 çift gerekir.")])
    with MCPClient() as tools:
        answer = Agent(model, tools, log).ask(question)

    assert answer == "45 çift gerekir."
    (line,) = read_log(log)
    assert list(line) == LOG_FIELDS
    assert line["question"] == question
    assert line["tool_input"] == PAIRED
    assert line["tool_output"] == call_tool("power_analysis", PAIRED)  # hesap motordan
    assert line["tool_output"]["n_total"] == 45
    assert (line["tokens_in"], line["tokens_out"]) == (100, 20)
    assert re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d[+-]\d\d:\d\d", line["ts"])

    # Araç sonucu modele functionResponse olarak döner.
    last_turn = model.seen[1][-1]
    assert last_turn["parts"][0]["functionResponse"]["response"]["n_total"] == 45


def test_medium_effect_is_not_assumed(tmp_path):
    """§10: kullanıcı yalnızca "orta etki" dedi; model dz = 0.5 ile çağırmaya kalkarsa çağrı engellenir."""
    log = tmp_path / "agent_calls.jsonl"
    tools = RecordingTools()
    question = "Kurgusal önce-sonra çalışması: orta etki, tek yönlü, alpha 0.05, güç 0.95. Kaç çift gerekir?"
    model = FakeModel([call_reply(PAIRED),
                       text_reply("Orta etki için dz = 0.5 kullanayım mı?")])
    answer = Agent(model, tools, log).ask(question)

    assert answer == "Orta etki için dz = 0.5 kullanayım mı?"
    assert tools.calls == []  # motor çağrılmadı
    assert not log.exists()   # araca ulaşmayan çağrı loglanmaz
    rejection = model.seen[1][-1]["parts"][0]["functionResponse"]["response"]
    assert rejection["code"] == "NOT_STATED"
    assert rejection["fields"] == ["dz"]


def test_confirmed_proposal_is_allowed(tmp_path):
    """Ajan 0.5'i önerdi, kullanıcı "evet" dedi: değer artık kullanıcı onaylı."""
    log = tmp_path / "agent_calls.jsonl"
    tools = RecordingTools()
    model = FakeModel([text_reply("Orta etki için dz = 0.5 kullanayım mı?"),
                       call_reply(PAIRED, tokens_in=300, tokens_out=40),
                       text_reply("45 çift gerekir.")])
    agent = Agent(model, tools, log)
    agent.ask("Kurgusal önce-sonra çalışması: orta etki, tek yönlü, alpha 0.05, güç 0.95.")
    assert agent.ask("evet") == "45 çift gerekir."

    assert tools.calls == [PAIRED]
    (line,) = read_log(log)
    assert "evet" in line["question"] and "orta etki" in line["question"]
    assert (line["tokens_in"], line["tokens_out"]) == (300, 40)


def test_unconfirmed_proposal_is_still_blocked(tmp_path):
    tools = RecordingTools()
    model = FakeModel([text_reply("Orta etki için dz = 0.5 kullanayım mı?"),
                       call_reply(PAIRED), text_reply("Hangi dz değerini kullanalım?")])
    agent = Agent(model, tools, tmp_path / "log.jsonl")
    agent.ask("Kurgusal önce-sonra çalışması: orta etki, tek yönlü, alpha 0.05, güç 0.95.")
    agent.ask("emin değilim")
    assert tools.calls == []


def test_missing_tails_is_not_assumed(tmp_path):
    tools = RecordingTools()
    model = FakeModel([call_reply(PAIRED), text_reply("Tek yönlü mü, çift yönlü mü?")])
    Agent(model, tools, tmp_path / "log.jsonl").ask("Kurgusal çalışma: dz 0.5, alpha 0.05, güç 0.95.")
    assert tools.calls == []
    rejection = model.seen[1][-1]["parts"][0]["functionResponse"]["response"]
    assert rejection["fields"] == ["tails"]


def test_tool_error_is_logged_as_returned(tmp_path):
    """Eksik alanlı çağrı motora ulaşır; hata JSON'u olduğu gibi loglanır ve modele döner."""
    log = tmp_path / "agent_calls.jsonl"
    args = {k: v for k, v in PAIRED.items() if k != "power"}
    model = FakeModel([call_reply(args), text_reply("Güç değeri eksik.")])
    Agent(model, RecordingTools(), log).ask("Kurgusal çalışma: tek yönlü, dz 0.5, alpha 0.05.")
    (line,) = read_log(log)
    assert line["tool_output"]["code"] == "MISSING_PARAM"
    assert line["tool_output"]["field"] == "power"


def test_unknown_tool_is_rejected_without_logging(tmp_path):
    log = tmp_path / "agent_calls.jsonl"
    tools = RecordingTools()
    model = FakeModel([ModelReply("", [FunctionCall("calculator", {"x": 1})], 10, 5, None),
                       text_reply("Bu aracı kullanamam.")])
    Agent(model, tools, log).ask("tek yönlü dz 0.5")
    assert tools.calls == [] and not log.exists()


def test_step_limit_stops_runaway_loop(tmp_path):
    model = FakeModel([call_reply({"test": "t-paired"})] * 10)
    answer = Agent(model, RecordingTools(), tmp_path / "log.jsonl", max_steps=3).ask("tek yönlü")
    assert "adım" in answer.lower()


# --- Değer kaynağı denetimi --------------------------------------------------------------------

@pytest.mark.parametrize("text, value", [
    ("alfa %5", 0.05), ("güç %95", 0.95), ("95% power", 0.95), ("dz 0,5", 0.5),
    ("f2 = .15", 0.15), ("50 hasta", 50), ("alpha=0.05", 0.05),
])
def test_stated_numbers(text, value):
    assert any(abs(n - value) < 1e-12 for n in stated_numbers(text))


def test_ungrounded_fields_checks_numbers_and_tails():
    texts = ["tek yönlü, dz 0.5, alpha 0.05, güç 0.95"]
    assert ungrounded_fields(PAIRED, texts) == []
    assert ungrounded_fields({**PAIRED, "tails": 2}, texts) == ["tails"]
    assert ungrounded_fields({**PAIRED, "dz": 0.8}, texts) == ["dz"]
    # "2 yordayıcı" içindeki 2, kuyruk sayısı sayılmaz.
    assert ungrounded_fields({"tails": 2}, ["2 yordayıcı"]) == ["tails"]
    assert ungrounded_fields({"tails": 2}, ["çift yönlü"]) == []


# --- Gemini istemcisi (ağ yok) -----------------------------------------------------------------

class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_gemini_request_and_response_parsing():
    captured = {}
    reply_body = {
        "candidates": [{"content": {"role": "model", "parts": [
            {"functionCall": {"name": "power_analysis", "args": PAIRED}, "thoughtSignature": "sig"}]}}],
        "usageMetadata": {"promptTokenCount": 812, "candidatesTokenCount": 37},
    }

    def opener(request, timeout):
        captured["url"] = request.full_url
        captured["headers"] = dict(request.header_items())
        captured["body"] = json.loads(request.data)
        return FakeResponse(json.dumps(reply_body).encode())

    model = GeminiModel(FAKE_KEY, "gemini-test", opener=opener)
    reply = model.generate("sistem", [{"role": "user", "parts": [{"text": "soru"}]}],
                           [POWER_ANALYSIS_TOOL_SCHEMA])

    assert FAKE_KEY not in captured["url"]  # anahtar URL'de değil, başlıkta
    assert captured["headers"]["X-goog-api-key"] == FAKE_KEY
    assert captured["url"].endswith("/models/gemini-test:generateContent")
    assert captured["body"]["systemInstruction"]["parts"][0]["text"] == "sistem"
    (decl,) = captured["body"]["tools"][0]["functionDeclarations"]
    assert decl["name"] == "power_analysis"
    assert reply.calls == [FunctionCall("power_analysis", PAIRED)]
    assert (reply.tokens_in, reply.tokens_out) == (812, 37)
    assert reply.content["parts"][0]["thoughtSignature"] == "sig"  # geçmişe aynen döner


def test_declaration_drops_non_string_enums():
    decl = to_declaration(POWER_ANALYSIS_TOOL_SCHEMA)
    props = decl["parameters"]["properties"]
    assert "enum" not in props["tails"]
    assert props["test"]["enum"] == list(POWER_ANALYSIS_TOOL_SCHEMA["inputSchema"]["properties"]["test"]["enum"])


# --- Anahtar güvenliği -------------------------------------------------------------------------

def test_settings_prefer_environment_then_env_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text('# yorum\nGEMINI_API_KEY="dosyadaki"\nGEMINI_MODEL=model-dosya\n', encoding="utf-8")
    assert load_settings({}, [env_file]).api_key == "dosyadaki"
    assert load_settings({}, [env_file]).model == "model-dosya"
    assert load_settings({"GEMINI_API_KEY": "ortamdaki"}, [env_file]).api_key == "ortamdaki"


def test_missing_key_message_does_not_leak(tmp_path):
    with pytest.raises(ConfigError) as exc:
        load_settings({}, [tmp_path / "yok.env"])
    assert "GEMINI_API_KEY" in str(exc.value)


def test_key_never_reaches_log(tmp_path, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", FAKE_KEY)
    log = tmp_path / "agent_calls.jsonl"
    model = FakeModel([call_reply(PAIRED), text_reply("45")])
    Agent(model, RecordingTools(), log).ask("tek yönlü, dz 0.5, alpha 0.05, güç 0.95")
    assert FAKE_KEY not in log.read_text(encoding="utf-8")


def test_env_file_is_git_ignored():
    for name in (".env", ".env.local"):
        result = subprocess.run(["git", "check-ignore", "-q", name], cwd=REPO)
        assert result.returncode == 0, f"{name} .gitignore'da olmalı"
    result = subprocess.run(["git", "check-ignore", "-q", ".env.example"], cwd=REPO)
    assert result.returncode == 1, ".env.example repoda kalmalı (şablon)"


def test_no_api_key_in_tracked_files():
    tracked = subprocess.run(["git", "grep", "-I", "-l", "-E", r"AIza[0-9A-Za-z_-]{35}"],
                             cwd=REPO, capture_output=True, text=True)
    assert tracked.stdout == "", f"Repoda API anahtarına benzeyen metin var: {tracked.stdout}"
