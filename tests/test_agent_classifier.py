"""
tests/test_agent_classifier.py
Yönergenin "Sistem 1" adımı: test ailesi sınıflandırıcısı (Jev yerine etiket setine kısıtlı LLM).
Sınıflandırıcı sayı üretmez; güven < 0.75 ya da ambiguous / unsupported ise karar araştırmacıya sorulur.
Ayrıca: Gemini JSON isteği ve hız sınırında (429) yeniden deneme. Ağ ve gerçek model kullanılmaz.
"""

import io
import json
import urllib.error

import pytest

from powerlab.agent.agent import Agent
from powerlab.agent.classifier import CONFIDENCE_THRESHOLD, LABELS, Classification, FamilyClassifier
from powerlab.agent.gemini import FunctionCall, GeminiModel, ModelReply
from powerlab.mcp_server import POWER_ANALYSIS_TOOL_SCHEMA, call_tool

PAIRED = {"test": "t-paired", "mode": "a-priori", "tails": 1, "dz": 0.5, "alpha": 0.05, "power": 0.95}
QUESTION = "Kurgusal önce-sonra çalışması: tek yönlü, dz 0.5, alpha 0.05, güç 0.95. Kaç çift?"


class FakeModel:
    def __init__(self, replies):
        self.replies = list(replies)
        self.systems = []

    def generate(self, system, contents, tools):
        self.systems.append(system)
        return self.replies.pop(0)


class FakeClassifier:
    def __init__(self, *results):
        self.results = list(results)
        self.questions = []

    def classify(self, question):
        self.questions.append(question)
        return self.results.pop(0)


class Tools:
    def __init__(self):
        self.calls = []

    def list_tools(self):
        return [POWER_ANALYSIS_TOOL_SCHEMA]

    def call(self, arguments):
        self.calls.append(arguments)
        return call_tool("power_analysis", arguments)


def json_model(text, tokens=(40, 8)):
    class M:
        def generate_json(self, system, question, schema):
            self.schema = schema
            return ModelReply(text=text, calls=[], tokens_in=tokens[0], tokens_out=tokens[1], content=None)
    return M()


# --- Sınıflandırıcı ----------------------------------------------------------------------------

def test_classifier_reads_label_and_confidence():
    model = json_model('{"label": "t-paired", "confidence": 0.93}')
    result = FamilyClassifier(model).classify("önce-sonra")
    assert result == Classification("t-paired", 0.93, 40, 8)
    assert model.schema["properties"]["label"]["enum"] == list(LABELS)
    assert not result.needs_researcher


@pytest.mark.parametrize("text", ["bozuk", '{"label": "chi2"}', '{"label": "uydurma", "confidence": 0.9}'])
def test_classifier_falls_back_to_ambiguous(text):
    result = FamilyClassifier(json_model(text)).classify("soru")
    assert (result.label, result.confidence) == ("ambiguous", 0.0)
    assert result.needs_researcher


def test_needs_researcher_threshold():
    assert Classification("t-paired", CONFIDENCE_THRESHOLD - 0.01, 0, 0).needs_researcher
    assert not Classification("t-paired", CONFIDENCE_THRESHOLD, 0, 0).needs_researcher
    assert Classification("ambiguous", 0.99, 0, 0).needs_researcher
    assert Classification("unsupported", 0.99, 0, 0).needs_researcher


# --- Ajan ile birlikte -------------------------------------------------------------------------

def test_low_confidence_asks_researcher_without_calling_model(tmp_path):
    model, tools = FakeModel([]), Tools()
    agent = Agent(model, tools, tmp_path / "log.jsonl", classifier=FakeClassifier(Classification("t-paired", 0.6, 30, 5)))
    answer = agent.ask("Hastalarda fark var mı?")
    assert "t-paired" in answer and "0.60" in answer
    assert model.systems == [] and tools.calls == []


@pytest.mark.parametrize("label", ["ambiguous", "unsupported"])
def test_ambiguous_or_unsupported_asks_researcher(tmp_path, label):
    model = FakeModel([])
    agent = Agent(model, Tools(), tmp_path / "log.jsonl", classifier=FakeClassifier(Classification(label, 0.95, 30, 5)))
    assert label in agent.ask("soru")
    assert model.systems == []


def test_out_of_scope_family_is_not_computed(tmp_path):
    model = FakeModel([])
    agent = Agent(model, Tools(), tmp_path / "log.jsonl",
                  classifier=FakeClassifier(Classification("t2-indep", 0.9, 30, 5)))
    answer = agent.ask("İlaç ve plasebo iki bağımsız grup")
    assert "t2-indep" in answer and "kapsam" in answer.lower()
    assert model.systems == []


def test_clarification_is_reclassified_with_whole_conversation(tmp_path):
    classifier = FakeClassifier(Classification("ambiguous", 0.4, 30, 5), Classification("t-paired", 0.9, 30, 5))
    model = FakeModel([ModelReply("", [FunctionCall("power_analysis", PAIRED)], 100, 20, None),
                       ModelReply("45 çift.", [], 120, 10, None)])
    agent = Agent(model, Tools(), tmp_path / "log.jsonl", classifier=classifier)
    agent.ask("Fark var mı?")
    assert agent.ask(QUESTION) == "45 çift."
    assert "Fark var mı?" in classifier.questions[1] and QUESTION in classifier.questions[1]


def test_confident_label_is_passed_to_model_and_enforced(tmp_path):
    tools = Tools()
    wrong = {"test": "multireg-r2", "mode": "a-priori", "f2": 0.5, "alpha": 0.05, "power": 0.95, "predictors": 1}
    model = FakeModel([ModelReply("", [FunctionCall("power_analysis", wrong)], 100, 20, None),
                       ModelReply("Hangi test?", [], 50, 5, None)])
    agent = Agent(model, tools, tmp_path / "log.jsonl",
                  classifier=FakeClassifier(Classification("t-paired", 0.9, 30, 5)))
    agent.ask("Kurgusal önce-sonra, dz 0.5, f2 0.5, alpha 0.05, güç 0.95, 1 yordayıcı")
    assert "t-paired" in model.systems[0]
    assert tools.calls == []  # sınıflandırıcıyla çelişen aile araca gitmez


def test_usage_totals_include_classifier(tmp_path):
    model = FakeModel([ModelReply("", [FunctionCall("power_analysis", PAIRED)], 100, 20, None),
                       ModelReply("45", [], 120, 10, None)])
    log = tmp_path / "log.jsonl"
    agent = Agent(model, Tools(), log, classifier=FakeClassifier(Classification("t-paired", 0.9, 30, 5)))
    agent.ask(QUESTION)
    assert (agent.tokens_in, agent.tokens_out) == (30 + 100 + 120, 5 + 20 + 10)
    line = json.loads(log.read_text(encoding="utf-8"))
    assert (line["tokens_in"], line["tokens_out"]) == (130, 25)  # sınıflandırıcı + çağrıyı üreten yanıt


# --- Gemini: JSON isteği ve yeniden deneme -----------------------------------------------------

class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def ok_body(text='{"label": "t-paired", "confidence": 0.9}'):
    return json.dumps({"candidates": [{"content": {"role": "model", "parts": [{"text": text}]}}],
                       "usageMetadata": {"promptTokenCount": 11, "candidatesTokenCount": 3}}).encode()


def test_generate_json_requests_schema_without_tools():
    bodies = []

    def opener(request, timeout):
        bodies.append(json.loads(request.data))
        return FakeResponse(ok_body())

    reply = GeminiModel("anahtar", "m", opener=opener).generate_json("sistem", "soru", {"type": "object"})
    assert bodies[0]["generationConfig"] == {"responseMimeType": "application/json",
                                             "responseSchema": {"type": "object"}}
    assert "tools" not in bodies[0]
    assert json.loads(reply.text)["label"] == "t-paired"


def test_rate_limit_is_retried():
    attempts, sleeps = [], []

    def opener(request, timeout):
        attempts.append(1)
        if len(attempts) == 1:
            raise urllib.error.HTTPError(request.full_url, 429, "Too Many Requests", {},
                                         io.BytesIO(b'{"error": {"message": "quota"}}'))
        return FakeResponse(ok_body())

    model = GeminiModel("anahtar", "m", opener=opener, sleep=sleeps.append)
    model.generate_json("s", "q", {"type": "object"})
    assert len(attempts) == 2 and sleeps == [5.0]
