# eval/_eski — eski çalıştırma, GEÇERSİZ

`agent_calls.jsonl` dosyası 2026-10-19'daki ilk ajan çalıştırmasının günlüğüdür ve **geçersizdir**:

- Beklenen etiketler ve `expected_n` değerleri ajanla aynı oturumda yazıldı; hiçbir kâhinle
  doğrulanmadı.
- Çalıştırmayı yapan `evaluate_agent.py` o sırada "4/4" sonucunu koda sabit yazılmış olarak
  basıyordu (bkz. HALLUCINATIONS.md H05).
- Kayıtlar, sonradan değişen CLI/MCP sözleşmesinden (CONTRACT_ASSUMED.md) önceki davranışı yansıtır.

Dosya yalnızca geçmişi göstermek için saklanıyor. JSONL biçimi bozulmasın diye not dosyanın içine
değil buraya yazıldı. Yeni çalıştırmalar `eval/agent_calls.jsonl` dosyasına yazılır.
