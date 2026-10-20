# CLAUDE.md — Proje kuralları

Bu dosya yalnızca çalışma kurallarını içerir; inceleme bulgusu içermez.

## Kâhin
- Kâhin G*Power'dır. Ekran görüntüsü olmayan değer kâhin değildir ve **asla uydurulmaz**.
- `oracle/gpower_vectors.csv` içindeki bir beklenen değer, ancak `oracle/screenshots/` altında ona
  karşılık gelen ekran görüntüsü varsa doldurulur. Değer bilinmiyorsa alan boş bırakılır.

## Kâhin vektörü işleme ("Vxx–Vyy hazır" dendiğinde)
Ekran görüntüleri `oracle/screenshots/Vxx.png` adıyla kaydedilir; girilecek vektörler
`oracle/TOPLAMA_LISTESI.md` içindedir. Kullanıcı bir grubun hazır olduğunu söylediğinde:

1. **Oku.** Her görüntüyü aç; girdileri (Type of power analysis, Tail(s), Effect size dz, α err prob,
   Power ya da Total sample size) ve 5 çıktıyı (Noncentrality parameter δ, Critical t, Df,
   Total sample size, Actual power) ekranda görüldüğü gibi, **metin olarak aynen** çıkar (sondaki
   sıfırlar dahil). G*Power uyarı/hata verdiyse tepkiyi aynen not et.
2. **Girdileri doğrula.** Görüntüdeki girdiler TOPLAMA_LISTESI'ndekiyle birebir aynı mı? Test
   ailesi `t tests / Means: Difference between two dependent means (matched pairs)` mı? Farklıysa
   o vektörü **doldurma**, kullanıcıya bildir. Görüntü okunaksız ya da eksikse de doldurma.
3. **Önce göster.** Okunan değerleri tablo olarak kullanıcıya göster. Kullanıcı **"onay"** demeden
   CSV'ye yazma ve commit etme (okuma hatası riskine karşı insan kontrolü).
4. **Onaydan sonra yaz.** Değerleri `oracle/gpower_vectors.csv`'ye metin olarak aynen yaz,
   `screenshot` sütununa dosya adını gir, `oracle/generate_toplama_listesi.py` ile listeyi
   yeniden üret ([x]) ve commit et.
5. **Test et.** Diferansiyel testi (`pytest tests/test_differential.py`) çalıştır ve uyum raporunu
   yeniden üret; uyuşmazlıkları vektör vektör raporla.
6. **Beklenen değeri ASLA motora göre düzeltme.** Uyuşmazlık bir bulgudur: önce "spec'te mi eksik,
   kodda mı hata?" diye sor, LEDGER'a gözlem olarak ekle; CSV'deki kâhin değeri değişmez.

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
