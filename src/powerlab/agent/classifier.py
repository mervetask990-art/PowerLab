"""
src/powerlab/agent/classifier.py
Test ailesi sınıflandırıcısı (yönergedeki "Sistem 1" adımı). Jev erişimi olmadığı için aynı etiket setine
kısıtlanmış bir LLM kullanılır: Gemini, JSON şemasıyla yalnızca {"label", "confidence"} döndürür.

Sınıflandırıcı hiçbir sayı üretmez; N, güç ve etki büyüklüğü yalnızca motordan gelir. Güven 0.75'in altındaysa
ya da etiket ambiguous / unsupported ise karar araştırmacıya sorulur (agent.Agent).
"""

import json
from dataclasses import dataclass

LABELS = ("t2-indep", "t-paired", "anova-oneway", "chi2-contingency", "multireg-r2", "ambiguous", "unsupported")
IMPLEMENTED = ("t-paired", "multireg-r2")
CONFIDENCE_THRESHOLD = 0.75

SCHEMA = {
    "type": "object",
    "properties": {
        "label": {"type": "string", "enum": list(LABELS)},
        "confidence": {"type": "number"},
    },
    "required": ["label", "confidence"],
}

SYSTEM_PROMPT = """\
Bir klinik araştırma sorusunun hangi istatistiksel güç analizi ailesine ait olduğunu sınıflandırırsın.
Yalnızca etiket ve 0 ile 1 arasında güven döndür; hiçbir sayı hesaplama.
- t2-indep: iki bağımsız grubun ortalamaları (ör. ilaç ve plasebo grupları)
- t-paired: aynı deneklerde eşleştirilmiş iki ölçüm (ör. önce-sonra, aynı hastada iki ölçüm)
- anova-oneway: üç ya da daha fazla bağımsız grubun ortalamaları (tek yönlü ANOVA)
- chi2-contingency: kategorik oranlar, olumsallık tablosu (ki-kare)
- multireg-r2: çoklu doğrusal regresyon, R² sıfırdan sapma (birden çok yordayıcı / risk faktörü)
- ambiguous: tasarım bu ailelerden birini seçmeye yetmiyor
- unsupported: bu ailelerin hiçbiri değil (ör. Wilcoxon, Mann-Whitney, sağkalım, lojistik regresyon)
Güven, etiketin doğru olma olasılığına dair dürüst tahminin olsun.
"""


@dataclass(frozen=True)
class Classification:
    label: str
    confidence: float
    tokens_in: int
    tokens_out: int

    @property
    def needs_researcher(self) -> bool:
        return self.confidence < CONFIDENCE_THRESHOLD or self.label in ("ambiguous", "unsupported")


class FamilyClassifier:
    def __init__(self, model):
        self.model = model

    def classify(self, question: str) -> Classification:
        reply = self.model.generate_json(SYSTEM_PROMPT, question, SCHEMA)
        try:
            data = json.loads(reply.text)
            label, confidence = data["label"], float(data["confidence"])
        except (ValueError, KeyError, TypeError):
            label, confidence = "ambiguous", 0.0
        if label not in LABELS:
            label, confidence = "ambiguous", 0.0
        confidence = min(max(confidence, 0.0), 1.0)
        return Classification(label, confidence, reply.tokens_in, reply.tokens_out)
