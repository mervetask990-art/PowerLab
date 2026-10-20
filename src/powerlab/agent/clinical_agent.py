"""
src/powerlab/agent/clinical_agent.py
Türkçe ve İngilizce klinik soruları analiz eden kural ve çıkarım tabanlı akıllı klinik ajan döngüsü.
Kural: Ajan hiçbir sayı HESAPLAMAZ! N, güç, df yalnızca motordan gelir.
Güven < 0.75 veya ambiguous/unsupported durumunda araştırmacıya yönlendirici soru sorar.
Tüm araç çağrılarını JSONL dosyasına kaydeder.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

from powerlab.mcp_server import call_tool

LOG_FILE = Path("eval/agent_calls.jsonl")


class ClinicalAgent:
    def __init__(self, log_path: Optional[Path] = None):
        self.log_path = log_path or LOG_FILE
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def extract_intent(self, question: str) -> Dict[str, Any]:
        """
        Doğal dildeki klinik sorudan test ailesini, parametreleri ve güven skorunu çıkarır.
        Etiketler: t-paired, t2-indep, anova-oneway, chi2-contingency, multireg-r2, ambiguous, unsupported
        """
        text = question.lower().strip()

        # 1. Desteklenmeyen (Non-parametrik, survival vb.) durum kontrolü
        unsupported_keywords = [
            "mann-whitney", "wilcoxon", "kruskal", "kaplan-meier", "cox", "sağkalım",
            "survival", "non-parametric", "nonparametrik", "lojistik regresyon", "logistic"
        ]
        for kw in unsupported_keywords:
            if kw in text:
                return {
                    "label": "unsupported",
                    "confidence": 0.95,
                    "reason": f"Soru desteklenmeyen '{kw}' analizini içermektedir.",
                    "params": {}
                }

        # 2. Belirsiz (Ambiguous) soru kontrolü (kısa ve içeriği belirsiz sorular)
        if len(text.split()) < 5 or ("fark var mıdır" in text and "önce" not in text and "grup" not in text and "doz" not in text and "regresyon" not in text):
            return {
                "label": "ambiguous",
                "confidence": 0.40,
                "reason": "Yetersiz klinik bağlam ve tasarım detayı.",
                "params": {}
            }

        # 3. Test ailesi tespiti
        label = "ambiguous"
        confidence = 0.50

        # Eşleştirilmiş t-testi göstergeleri (t-paired)
        paired_signals = [
            "önce ve sonra", "önce-sonra", "öncesi ve sonrası", "öncesi ve tedavi sonrası",
            "pre-post", "before and after", "eşleştirilmiş", "bağımlı", "aynı hastalar",
            "aynı denekler", "tekrarlı ölçüm", "matched pairs", "dependent means", "tansiyon önce"
        ]
        
        # İki bağımsız grup t-testi göstergeleri (t2-indep)
        indep_signals = [
            "iki bağımsız grup", "kontrol ve deney grubu", "tedavi ve plasebo",
            "kadın ve erkek", "independent samples", "two independent groups", "iki ayrı grup"
        ]

        # Tek yönlü anova (anova-oneway)
        anova_signals = ["üç grup", "4 grup", "üç farklı doz", "dörtten fazla grup", "one-way anova", "tek yönlü anova"]

        # Ki-kare (chi2-contingency)
        chi2_signals = ["kontenjans", "oran karşılaştırması", "bağımsızlık testi", "chi-square", "ki-kare", "oranlar arası fark"]

        # Çoklu regresyon (multireg-r2)
        reg_signals = ["çoklu regresyon", "multiple regression", "r2", "r-kare", "bağımsız değişkenle yordama"]

        if any(s in text for s in paired_signals) or ("önce" in text and "sonra" in text):
            label = "t-paired"
            confidence = 0.92
        elif any(s in text for s in indep_signals) or ("bağımsız" in text and "grup" in text):
            label = "t2-indep"
            confidence = 0.90
        elif any(s in text for s in anova_signals):
            label = "anova-oneway"
            confidence = 0.88
        elif any(s in text for s in chi2_signals):
            label = "chi2-contingency"
            confidence = 0.88
        elif any(s in text for s in reg_signals):
            label = "multireg-r2"
            confidence = 0.88
        else:
            label = "ambiguous"
            confidence = 0.45

        # 4. Parametre Çıkarımı
        params: Dict[str, Any] = {"tails": 2, "alpha": 0.05, "power": 0.80}

        # Tek / Çift kuyruk
        if any(w in text for w in ["tek yönlü", "tek kuyruk", "one-tailed", "one tail", "üstünlük"]):
            params["tails"] = 1
        else:
            params["tails"] = 2

        # Alfa (alpha)
        alpha_match = re.search(r"(?:alfa|alpha|p)\s*[:=]?\s*(0\.\d+)", text)
        if alpha_match:
            params["alpha"] = float(alpha_match.group(1))
        elif "%5" in text or "5%" in text:
            params["alpha"] = 0.05
        elif "%1" in text or "1%" in text:
            params["alpha"] = 0.01

        # Güç (power)
        power_match = re.search(r"(?:güç|power|1-beta)\s*[:=]?\s*(0\.\d+|\d+)", text)
        pct_power = re.search(r"(?:%(\d+)\s*güç|(\d+)%\s*power)", text)
        if pct_power:
            pct_val = float(pct_power.group(1) or pct_power.group(2))
            params["power"] = pct_val / 100.0 if pct_val > 1.0 else pct_val
        elif power_match:
            val_str = power_match.group(1)
            val = float(val_str)
            params["power"] = val / 100.0 if val > 1.0 else val

        # Etki büyüklüğü (dz veya d)
        d_match = re.search(r"(?:dz|d|etki büyüklüğü|effect size)\s*[:=]?\s*(0\.\d+|\d+\.\d+)", text)
        if d_match:
            params["dz"] = float(d_match.group(1))
        else:
            # Standart Cohen sözel tanımları
            if any(w in text for w in ["orta etki", "medium effect"]):
                params["dz"] = 0.5
            elif any(w in text for w in ["küçük etki", "small effect"]):
                params["dz"] = 0.2
            elif any(w in text for w in ["büyük etki", "large effect"]):
                params["dz"] = 0.8

        return {
            "label": label,
            "confidence": confidence,
            "params": params,
            "reason": f"Metindeki anahtar klinik sinyaller tespit edildi ({label})."
        }

    def process_query(self, question: str) -> Dict[str, Any]:
        """
        Klinik soruyu işler, gerekirse araç çağırır ve JSONL formatında loglar.
        """
        start_time = datetime.now()
        intent = self.extract_intent(question)
        label = intent["label"]
        conf = intent["confidence"]
        params = intent["params"]

        response_payload: Dict[str, Any] = {
            "question": question,
            "extracted_family": label,
            "confidence": conf,
            "timestamp": datetime.now().isoformat(),
        }

        # Kural: Güven < 0.75 veya ambiguous / unsupported ise araştırmacıya yönelt
        if conf < 0.75 or label in ("ambiguous", "unsupported"):
            response_payload["status"] = "clarification_needed"
            if label == "unsupported":
                response_payload["message"] = (
                    f"Belirtilen analiz ({label}) standart parametrik test ailemiz kapsamında desteklenmemektedir. "
                    f"Parametrik eşleniği (örneğin Wilcoxon yerine t-paired) kullanmak ister misiniz?"
                )
            else:
                response_payload["message"] = (
                    "Klinik araştırma sorunuzda tasarım detayları belirsizdir. "
                    "Çalışmanız aynı hastaların önce/sonra ölçümüne mi (t-paired), yoksa iki ayrı bağımsız hasta grubuna mı (t2-indep) dayanıyor?"
                )
            self._log_call(response_payload)
            return response_payload

        # Kural: Ajan hesaplama yapmaz, MCP aracını çağırır
        tool_args = {
            "test": label,
            "mode": "a-priori",
            "tails": params.get("tails", 2),
            "alpha": params.get("alpha", 0.05),
            "power": params.get("power", 0.80),
            "dz": params.get("dz", 0.5)
        }

        tool_result = call_tool("power_analysis", tool_args)
        response_payload["status"] = "tool_executed"
        response_payload["tool_args"] = tool_args
        response_payload["tool_result"] = tool_result

        duration_ms = (datetime.now() - start_time).total_seconds() * 1000.0
        response_payload["duration_ms"] = round(duration_ms, 2)

        self._log_call(response_payload)
        return response_payload

    def _log_call(self, payload: Dict[str, Any]) -> None:
        """Tüm araç ve ajan döngüsü çağrılarını JSONL formatına yazar."""
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
