# HALLUCINATIONS: Hallüsinasyon ve Yanılgı Defteri

Bu dosya, yapay zeka ajanının ürettiği yanlış iddiaları, bunların nasıl fark edildiğini ve hangi
kontrolün yakaladığını belgeler.

**Kaynak**: Salt okunur proje denetimi (2026-10-20). Satır referansları snapshot commit'ine aittir:
`d7b36b3` ("snapshot: denetim öncesi durum"). Örn. `d7b36b3:SPEC.md:69`.

> Önceki H01–H04 kayıtları kaldırıldı: hepsi "G*Power şunu üretti / bildirdi" diyordu ama repoda
> tek bir G*Power ekran görüntüsü yoktu (`oracle/screenshots/` boş). Yani yakalandıkları söylenen
> hatalar doğrulanabilir bir kâhine dayanmıyordu. Orijinal metin `d7b36b3:HALLUCINATIONS.md`
> içinde duruyor.

---

### H01: Ekran görüntüsü olmadan "G*Power değeri" olarak yazılan 0.9531
- **Ne iddia edildi**: V01 (dz=0.5, α=0.05, güç=0.95, iki kuyruk) için G*Power'ın actual power
  değerinin 0.9531 / 0.953103 olduğu söylendi (`d7b36b3:SPEC.md:69`, `d7b36b3:README.md:121`,
  `d7b36b3:oracle/gpower_vectors.csv:2`, `d7b36b3:LEDGER.md` L06).
- **Nasıl fark edildi**: CSV'de anılan `s01_standard_d05_p95.png` dosyası yok. Aynı satırdaki
  `critical` ve `ncp` değerleri scipy çıktısıyla 6 basamağa kadar birebir aynı, `actual_power` ise
  farklı. Motor 0.950212 üretiyor; `test_cli_contract.py:38` 0.950212 bekliyor ve eski H04 de
  0.9531'i "yanlış" ilan ediyordu. Kısacası repo kendi içinde çelişiyordu.
- **Hangi kontrol yakaladı**: Denetimde CLI'nin gerçekten çalıştırılması ve çıktının
  SPEC/README/CSV ile karşılaştırılması. Otomatik bir test yakalamadı, çünkü CSV hiç yüklenmiyordu (bkz. H03).
- **Düzeltme**: Değerler `oracle/_dogrulanmamis/legacy_vectors.csv` dosyasına taşındı. SPEC'te
  V01–V03 beklentileri "G*Power ile doğrulanacak" olarak işaretlendi. LEDGER L06/L10 düzeltildi.
- **DOĞRULANDI: G*Power 0.9502120 gösteriyor (`oracle/screenshots/V01.png`).** 0.9531 / 0.953103
  değeri gerçekten yanlıştı. Ekrandaki diğer değerler: N=54, Df=53, δ=3.6742346, Critical t=2.0057460.
  Motorun 0.950212 sonucu doğruydu; ekran ayrıca çıktının 7 ondalık gösterildiğini ortaya koydu
  (LEDGER L11).

### H02: Kanıtsız [REA] etiketleri
- **Ne iddia edildi**: LEDGER L08 ve L10 (`d7b36b3:LEDGER.md:23,25`) GPower.exe binary'sinden
  kanıtlanmış ([REA]) bulgular olarak etiketlendi.
- **Nasıl fark edildi**: İki satırın "kanıt" sütununda da fonksiyon adresi ya da dize referansı yok.
  Kanıt olarak `scipy.stats.nct` denemesi ve projenin kendi diferansiyel testi gösterilmiş. Repoda
  Ghidra kullanımına dair hiçbir iz yok (adres, `FUN_`/`DAT_` araması sıfır sonuç verdi) ve makinede
  Java kurulu değil.
- **Hangi kontrol yakaladı**: Denetimde LEDGER satırlarının, prompt 01'deki "[REA] için adres veya
  dize referansı ŞART" kuralına göre tek tek okunması.
- **Düzeltme**: L08 ve L10 [AJAN] yapıldı, sonlarına "(kanıt bekleniyor: Ghidra)" eklendi.

### H03: 0 vektör yüklenmesine rağmen "diferansiyel testler geçti" denmesi
- **Ne iddia edildi**: G*Power vektörlerine karşı diferansiyel testin geçtiği söylendi (README
  Katman 4: "%90 kapısı aşıldı").
- **Nasıl fark edildi**: CSV başlığı `# ID` ile başlıyordu; loader ise `row.get("ID")` arıyordu
  (`d7b36b3:tests/test_differential.py:25`), dolayısıyla her satır atlandı. Ayrıca veri satırları 17,
  başlık 16 alandı; sütunlar bir kaydığı için `n_expected` boş okunuyor, `actual_power` alanına 54
  düşüyordu. Test hiçbir şey karşılaştırmadan "OK" verdi.
- **Hangi kontrol yakaladı**: Denetimde `load_gpower_vectors()` fonksiyonunun doğrudan çağrılması
  (sonuç: 0 vektör) ve ilk satırın `csv.DictReader` ile okunan anahtarlarının yazdırılması.
- **Düzeltme**: Şablon 16 sütunlu ve `#`siz hale getirildi. `test_differential.py` artık beklenen
  değeri dolu vektör yoksa açıkça **skip** veriyor; sessizce geçmiyor.

### H04: Dairesel kâhin ve %98.36'nın yanlış yorumu
- **Ne iddia edildi**: "%98.36 tam N eşleşmesi ile %90 kapısı aşıldı" denildi
  (`d7b36b3:tests/report/conformance.md:17`, README, AGENT_COST). Referans verinin statsmodels ile
  üretildiği söylendi (README ağacı: "statsmodels ile 500+ vektör").
- **Nasıl fark edildi**: `oracle/generate_reference_stats.py` statsmodels kullanmıyor; motorla aynı
  algoritmayı (kesikli N araması + `scipy.stats.nct`) yeniden uyguluyor. 1280 vektörün tamamı bu
  dosyadan geliyordu, yani oran G*Power uyumunu değil, kodun kendi kopyasıyla uyumunu ölçüyordu.
  Kalan 21 uyuşmazlık "Yuvarlama eşiği" diye açıklanmıştı. Gerçek neden şu: üretici betikte sol
  kuyruk NaN koruması yok (`d7b36b3:oracle/generate_reference_stats.py:24`). Örneğin REF_1246
  (dz=1.5, α=0.001, güç=0.95) için N=17'de `nct.cdf(-t_crit)` NaN dönüyor, bu yüzden betik 24'ü
  seçiyor.
- **Hangi kontrol yakaladı**: Denetimde üretici betiğin okunması ve uyuşmazlık örneklerinde
  `nct.sf` / `nct.cdf` değerlerinin elle hesaplanması.
- **Düzeltme**: Dosyanın adı `oracle/selfcheck_scipy.csv` yapıldı ve README'de kâhin olmadığı
  yazıldı. `conformance.md` artık G*Power kâhini (0 vektör, ölçülmedi) ile self-check'i ayrı
  bölümlerde raporluyor.

### H05: evaluate_agent.py'de sabit yazılmış "4/4" sonucu
- **Ne iddia edildi**: Ajan benchmark'ında "Hedef N Tam Eşleşen: 4/4 (%100)" sonucu raporlandı.
  Ayrıca MCP ile GUI arasında token, süre ve doğruluk karşılaştırması yapıldığı söylendi.
- **Nasıl fark edildi**: "4/4" bir f-string içine sabit yazılmıştı (`d7b36b3:eval/evaluate_agent.py:87`);
  hesaplanan `correct_n` değişkeni hiç kullanılmıyordu. Token tablosu da ölçüm değil, gömülü metindi
  (`d7b36b3:eval/evaluate_agent.py:96`). Üstelik `expected_n=15` (Q02, Q10) değeri hiçbir kâhinle
  doğrulanmamıştı.
- **Hangi kontrol yakaladı**: Denetimde `evaluate_agent.py` kaynağının okunması.
- **Düzeltme**: Sabit satır ve gömülü tablo kaldırıldı, yerine "henüz ölçülmedi" yazıldı. README'deki
  benchmark sonuçları da "henüz ölçülmedi" olarak değiştirildi.

### H06: "G*Power ile birebir aynı durma koşulu" kod yorumu
- **Ne iddia edildi**: `solve_n` docstring'inde "G*Power ile birebir aynı durma koşulunu ve kesikli
  tamsayı aramasını uygular" yazıyordu (`d7b36b3:src/powerlab/engine/families/t_paired.py:56`).
- **Nasıl fark edildi**: G*Power'ın durma koşuluna dair [REA] kanıtı yok (bkz. H02) ve G*Power
  çıktısıyla karşılaştırılmış tek bir vektör de yok (bkz. H03). İddia kodun içinde, gerçekmiş gibi
  duruyordu.
- **Hangi kontrol yakaladı**: Denetimde kod yorumlarının LEDGER kanıtlarıyla çapraz kontrolü.
- **Düzeltme**: Yorum, kuralın varsayım olduğunu ve LEDGER L06'ya bağlı olduğunu söyleyecek şekilde
  değiştirildi.
