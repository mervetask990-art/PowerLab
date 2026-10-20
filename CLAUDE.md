# CLAUDE.md — Proje kuralları

Bu dosya yalnızca çalışma kurallarını içerir; inceleme bulgusu içermez.

## Kâhin
- Kâhin G*Power'dır. Ekran görüntüsü olmayan değer kâhin değildir ve **asla uydurulmaz**.
- `oracle/gpower_vectors.csv` içindeki bir beklenen değer, ancak `oracle/screenshots/` altında ona
  karşılık gelen ekran görüntüsü varsa doldurulur. Değer bilinmiyorsa alan boş bırakılır.

## Kanıt etiketleri
- `[REA]` yalnızca adres ya da dize kanıtıyla yazılır. Kanıt yoksa etiket `[AJAN]` olur.

## CLI
- Varsayılan çıktı tek satır JSON'dur; uyarılar stderr'e gider.

## Mimari
- Hesap mantığı yalnızca `src/powerlab/engine/` içindedir. CLI, MCP ve ajan katmanları hesap
  yapmaz; yalnızca motoru çağırır.

## Temiz oda
- Decompile çıktısı repoya girmez.

## Testler
- Testler unittest yerine pytest ile çalışır: `pytest`
