# eval/_eski — eski çalıştırma, GEÇERSİZ

`agent_calls.jsonl` dosyası 2026-10-19'daki ilk ajan çalıştırmasının günlüğüdür ve **geçersizdir**:

- Beklenen etiketler ve `expected_n` değerleri ajanla aynı oturumda yazıldı; hiçbir kâhinle
  doğrulanmadı.
- Çalıştırmayı yapan `evaluate_agent.py` o sırada "4/4" sonucunu koda sabit yazılmış olarak
  basıyordu (bkz. HALLUCINATIONS.md H05).
- Kayıtlar, sonradan değişen CLI/MCP sözleşmesinden (CONTRACT_ASSUMED.md) önceki davranışı yansıtır.

Dosya yalnızca geçmişi göstermek için saklanıyor. JSONL biçimi bozulmasın diye not dosyanın içine
değil buraya yazıldı.

2026-10-25'te `evaluate_agent.py` ve `questions_tr.jsonl` de buraya taşındı. Kural tabanlı eski ajan
(`src/powerlab/agent/clinical_agent.py`, git geçmişinde) silindi; değer verilmediğinde `tails 2`,
`alpha 0.05`, `power 0.80` ve "orta etki" için `dz 0.5` değerlerini sessizce varsayıyordu
(CONTRACT.md §10'a aykırı). `questions_tr.jsonl` içindeki `expected_n` değerleri kâhinle doğrulanmamıştır.
Yeni ajan: `src/powerlab/agent/agent.py` (Gemini + MCP); log: `logs/agent_calls.jsonl` (CONTRACT.md §8).
