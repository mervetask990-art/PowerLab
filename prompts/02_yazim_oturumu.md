ROL: Kıdemli bir Python mühendisisin. Elinde yalnızca SPEC.md ve oracle/
altındaki referans vektörler var. Bunun dışında hiçbir kaynağa
(decompile çıktısı, orijinal kod) erişimin yok ve olmamalı.

HEDEF: SPEC.md'deki davranışı gerçekleyen bir güç analizi kütüphanesi ve CLI.
Proje adı "powerlab". Hiçbir yerde "G*Power" adını ürün adı olarak kullanma.

MİMARİ (zorunlu)
- src/powerlab/engine/: TEK hesap motoru; saf fonksiyonlar, yan etkisiz.
  distributions.py, solver.py, rounding.py, validation.py, families/t_paired.py
- src/powerlab/cli.py: yalnızca argparse + engine çağrısı + tek satır JSON.
- Hesap mantığı CLI/MCP içine KOPYALANMAZ.
- Dağılım fonksiyonları için scipy serbest (scipy.stats.nct, t); N araması, yuvarlama ve df
  hesabı bizim kodumuzdan gelir.

CLI SÖZLEŞMESİ
gpower-clone değil: komut adı "powerlab".
Örnek (A priori):
  powerlab --test t-paired --mode a-priori --tails 2 --dz 0.5 --alpha 0.05 --power 0.95
Çıktı (tek satır JSON):
  {"n":54,"n_total":54,"actual_power":0.9531,"critical":2.0057,"df":53,"ncp":3.6742}
Örnek (Post hoc):
  powerlab --test t-paired --mode post-hoc --tails 2 --dz 0.5 --alpha 0.05 --n 54
Hata:
  {"error":"..."} ve sıfırdan farklı çıkış kodu.

SÜREÇ (test güdümlü)
1. Önce SPEC.md'deki her Scenario için pytest testi yaz (başta hepsi kırmızı).
2. tests/test_differential.py: oracle/gpower_vectors.csv ve
   boundary_vectors.csv dosyalarını okuyup motoru karşılaştırır.
   N TAM eşleşmeli; diğer değerler (power, critical, ncp) CSV'deki basamak sayısına kadar eşleşmeli.
3. Sonra motoru yaz, testleri yeşile çek.
4. Uyuşmazlıkta ÖNCE sorun: "spec'te mi eksik, kodda mı hata?" Beklenen
   değeri ASLA testlerden uydurma; oracle neyse odur.
5. tests/report/conformance.md üret: toplam vektör, N tam eşleşme oranı,
   her uyuşmazlık için açıklama.
6. Her aşamada neyi neden yaptığını kısaca yaz; spec'te olmayan bir kuralı
   varsayman gerekirse bunu "VARSAYIM" olarak işaretle ve bana bildir.

KALİTE ÖLÇÜTLERİ
- Tür ipuçları, docstring, açıklayıcı hata mesajları.
- Sınır değerler: çok küçük/büyük dz, güç ≤ alpha,
  geçersiz girdiler (negatif, NaN, alpha ∉ (0,1), power ∉ (0,1), tails ∉ {1,2}).
- Deterministik çıktı; rastgelelik yok.
