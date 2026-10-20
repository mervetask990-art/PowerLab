# LEDGER: Kanıt Defteri (t-paired)

Bu defter, G*Power 3.1.9.7 davranışlarının kaynağını ve kanıt zincirini adım adım kayıt altına alır.

## Kanıt Etiketleri
- **`[DOK]`**: Resmi kılavuz, makale (Faul et al., 2007, 2009) veya istatistik literatürü.
- **`[REA]`**: GPower.exe binary'sinden Ghidra / x64dbg ile kanıtlanmış bulgu (fonksiyon adresi / dize referansı zorunlu).
- **`[AJAN]`**: Ajanın akıl yürütmesi / çıkarımı; tersine mühendislikle doğrulanana kadar hipotez statüsündedir.

---

## Kanıt Tablosu

| ID | Etiket | Kategori | İddia / Bulgu | Kanıt (Adres / Dize / Literatür) | Güven |
|---|---|---|---|---|---|
| L01 | [DOK] | Formül | t-paired için serbestlik derecesi df = N - 1'dir. | Faul et al. (2007) s. 180; Cohen (1988) | Yüksek (%100) |
| L02 | [DOK] | Formül | Merkezsizlik parametresi ncp delta = dz * sqrt(N)'dir. | Faul et al. (2007) denklem (4) | Yüksek (%100) |
| L03 | [DOK] | Dağılım | Güç hesabı noncentral t dağılımı kümülatif fonksiyonu (CDF) ile yapılır. | Faul et al. (2007) s. 177 | Yüksek (%100) |
| L04 | [AJAN] | Çözücü | A priori modda N, kesikli tamsayı arama (veya float N arayıp tavan tamsayıya yuvarlama) ile belirlenir. | statsmodels float N döndürürken G*Power her zaman tamsayı N verir. | Orta (%80) |
| L05 | [AJAN] | Çözücü | Çözücü N_min = 2'den başlar veya ikili arama (bisection) kullanır. | df = N - 1 >= 1 olmalıdır. | Orta (%75) |
| L06 | [AJAN] | Yuvarlama | G*Power'ın hedef güce ulaşan ilk tamsayıyı seçtiği varsayılır (Power(N) >= TargetPower); bu tavan yuvarlamaya denk gelir. | Kanıt yok; G*Power ekran görüntüsü bekleniyor (oracle V01). | Orta |
| L07 | [AJAN] | Sınır | dz <= 0 veya alpha <= 0 veya alpha >= 1 için GUI hesaplamayı reddeder ya da hata kutusu açar. | G*Power arayüz doğrulama davranış hipotezi | Yüksek (%90) |
| L08 | [AJAN] | Dağılım | Çift kuyrukta güç hesabının iki taraflı noncentral t kuyruğunu topladığı varsayılır: (1 - cdf(t_crit)) + cdf(-t_crit). Not: sol kuyruğun NaN dönmesi G*Power davranışı değil, scipy'ye özgü bir sayısal sorundur (motor 0.0 kabul eder). | Adres/dize yok; yalnızca scipy denemesi. (kanıt bekleniyor: Ghidra) | Orta |
| L09 | [DOK] | Fark | statsmodels.stats.power.ttest_power kesirli N verir; G*Power her zaman tamsayı N verir ve actual_power'ı bu tamsayı N ile günceller. | Faul et al. (2007) | Yüksek |
| L10 | [AJAN] | Çözücü | V01 girdileri (dz=0.5, α=0.05, güç=0.95, iki kuyruk) için MOTOR N=54, actual_power=0.950212 üretir. G*Power'ın bu girdiler için verdiği değer bilinmiyor; ekran görüntüsü gelene kadar L06'daki kural hipotezdir. | Adres/dize yok; motor çıktısıdır, kâhin değildir. (kanıt bekleniyor: Ghidra) | Düşük |
