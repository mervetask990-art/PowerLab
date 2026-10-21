"""
eval/evaluate_agent.py
eval/questions_tr.jsonl dosyasındaki 10 soruyu ajana sorarak
test ailesi seçim doğruluğunu, N eşleşmesini ve Türkçe/İngilizce performansını ölçer.
MCP ile GUI arasındaki token/süre karşılaştırması henüz ölçülmedi.
"""

import json
from pathlib import Path
from powerlab.agent.clinical_agent import ClinicalAgent

QUESTIONS_FILE = Path("eval/questions_tr.jsonl")
LOG_FILE = Path("eval/agent_calls.jsonl")


def main():
    if LOG_FILE.exists():
        LOG_FILE.unlink()  # Temiz başlangıç

    agent = ClinicalAgent(log_path=LOG_FILE)
    
    total = 0
    correct_family = 0
    correct_n = 0
    
    tr_total = 0
    tr_correct = 0
    en_total = 0
    en_correct = 0

    print("=" * 70)
    print("KLİNİK AJAN DEĞERLENDİRME VE BENCHMARK TESTİ (10 SORU)")
    print("=" * 70)

    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            total += 1
            qid = item["id"]
            lang = item["lang"]
            q_text = item["question"]
            exp_family = item["expected_family"]
            exp_n = item.get("expected_n")

            if lang == "tr":
                tr_total += 1
            else:
                en_total += 1

            res = agent.process_query(q_text)
            pred_family = res["extracted_family"]
            
            is_family_match = (pred_family == exp_family)
            if is_family_match:
                correct_family += 1
                if lang == "tr":
                    tr_correct += 1
                else:
                    en_correct += 1

            n_match_str = "-"
            if exp_n is not None and "n_total" in res.get("tool_result", {}):
                calc_n = res["tool_result"]["n_total"]
                if calc_n == exp_n:
                    correct_n += 1
                    n_match_str = f"TAM EŞLEŞTİ (N={calc_n})"
                else:
                    n_match_str = f"UYUŞMAZLIK (Hesaplanan={calc_n}, Beklenen={exp_n})"

            status = "[OK] BASARILI" if is_family_match else "[FAIL] YANLIS"
            print(f"[{qid}] [{lang.upper()}] {status} | Tahmin: {pred_family:<16} | Beklenen: {exp_family:<16} | N: {n_match_str}")

    fam_acc = (correct_family / total) * 100.0
    tr_acc = (tr_correct / tr_total) * 100.0 if tr_total > 0 else 0
    en_acc = (en_correct / en_total) * 100.0 if en_total > 0 else 0

    print("\n" + "=" * 70)
    print("ÖZET BAŞARI RAPORU")
    print("=" * 70)
    print(f"Toplam Soru Sayısı         : {total}")
    print(f"Doğru Aile Seçim Oranı     : %{fam_acc:.1f} ({correct_family}/{total})")
    print(f"Türkçe Soru Doğruluk Oranı : %{tr_acc:.1f} ({tr_correct}/{tr_total})")
    print(f"İngilizce Soru Doğruluk    : %{en_acc:.1f} ({en_correct}/{en_total})")
    print("Hedef N Tam Eşleşen        : henüz ölçülmedi (expected_n değerleri kâhinle doğrulanmadı)")
    print(f"Ajan Çağrı Log Dosyası     : {LOG_FILE}")

    print()
    print("TOKEN / SÜRE / DOĞRULUK KARŞILAŞTIRMASI (MCP vs. GUI): henüz ölçülmedi")


if __name__ == "__main__":
    main()
