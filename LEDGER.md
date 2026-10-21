# LEDGER: Kanıt Defteri (t-paired)

Bu defter, G*Power 3.1.9.7 davranışlarının kaynağını ve kanıt zincirini adım adım kayıt altına alır.

## Kanıt Etiketleri
- **`[DOK]`**: Resmi kılavuz, makale (Faul et al., 2007, 2009) veya istatistik literatürü.
- **`[REA]`**: GPower.exe binary'sinden Ghidra / x64dbg ile kanıtlanmış bulgu (fonksiyon adresi / dize referansı zorunlu).
- **`[AJAN]`**: Ajanın akıl yürütmesi / çıkarımı; tersine mühendislikle doğrulanana kadar hipotez statüsündedir.
- **`[KÂHİN]`** (KÂHİN GÖZLEMİ): G*Power arayüzünde gözlenen ve `oracle/screenshots/` altındaki ekran görüntüsüyle belgelenen davranış. Binary kanıtı değildir, **[REA] yerine geçmez**; "ne" olduğunu gösterir, "nasıl" olduğunu göstermez.

---

## Kanıt Tablosu

| ID | Etiket | Kategori | İddia / Bulgu | Kanıt (Adres / Dize / Literatür) | Güven |
|---|---|---|---|---|---|
| L01 | [DOK] | Formül | t-paired için serbestlik derecesi df = N - 1'dir. | Faul et al. (2007) s. 180; Cohen (1988) | Yüksek (%100) |
| L02 | [DOK] | Formül | Merkezsizlik parametresi ncp delta = dz * sqrt(N)'dir. | Faul et al. (2007) denklem (4) | Yüksek (%100) |
| L03 | [DOK] | Dağılım | Güç hesabı noncentral t dağılımı kümülatif fonksiyonu (CDF) ile yapılır. | Faul et al. (2007) s. 177 | Yüksek (%100) |
| L04 | [AJAN] | Çözücü | A priori modda N, kesikli tamsayı arama (veya float N arayıp tavan tamsayıya yuvarlama) ile belirlenir. | statsmodels float N döndürürken G*Power her zaman tamsayı N verir. | Orta (%80) |
| L05 | [AJAN] | Çözücü | Çözücü N_min = 2'den başlar veya ikili arama (bisection) kullanır. | df = N - 1 >= 1 olmalıdır. | Orta (%75) |
| L06 | [AJAN] | Yuvarlama | G*Power'ın hedef güce ulaşan ilk tamsayıyı seçtiği varsayılır (Power(N) >= TargetPower); bu tavan yuvarlamaya denk gelir. | V01 (L10) bu kuralla tutarlı: G*Power N=54'te 0.9502120 gösteriyor. N=53 için motor 0.9465273 hesaplıyor (bu kâhin değil, motor çıktısı). Tek veri noktası olduğu için kural kanıtlanmış sayılmaz. (kanıt bekleniyor: Ghidra) | Orta |
| L07 | [AJAN] | Sınır | dz <= 0 veya alpha <= 0 veya alpha >= 1 için GUI hesaplamayı reddeder ya da hata kutusu açar. | G*Power arayüz doğrulama davranış hipotezi | Yüksek (%90) |
| L08 | [AJAN] | Dağılım | Çift kuyrukta güç hesabının iki taraflı noncentral t kuyruğunu topladığı varsayılır: (1 - cdf(t_crit)) + cdf(-t_crit). Not: sol kuyruğun NaN dönmesi G*Power davranışı değil, scipy'ye özgü bir sayısal sorundur (motor 0.0 kabul eder). | Adres/dize yok; yalnızca scipy denemesi. (kanıt bekleniyor: Ghidra) | Orta |
| L09 | [DOK] | Fark | statsmodels.stats.power.ttest_power kesirli N verir; G*Power her zaman tamsayı N verir ve actual_power'ı bu tamsayı N ile günceller. | Faul et al. (2007) | Yüksek |
| L10 | [KÂHİN] | Çözücü | V01 (t-paired, a-priori, iki kuyruk, dz=0.5, α=0.05, güç=0.95): G*Power N=54, Df=53, δ=3.6742346, Critical t=2.0057460, Actual power=0.9502120 gösteriyor. Motor 7 basamakta beş değerin hepsini aynı üretiyor. | `oracle/screenshots/V01.png` | Yüksek (gözlem) |
| L11 | [KÂHİN] | Biçim | KÂHİN GÖZLEMİ: G*Power çıktıyı 7 ondalık basamakla gösterir (Output Parameters paneli; δ, Critical t, Actual power). Grafik başlığı ise `critical t = 2.00575` biçiminde 5 basamak gösteriyor. | `oracle/screenshots/V01.png` | Yüksek (gözlem) |
| L12 | [KÂHİN] | Sınır | KÂHİN GÖZLEMİ / UYUŞMAZLIK: V17 (a-priori, iki kuyruk, dz=0.5, α=0.05, güç=0.03): G*Power "Input error" kutusu açıyor: `Power must be greater than or equal to alpha.`; çıktı alanları `?`. Motor ise hata vermeden N=2 döndürüyor (V16 ile aynı çıktı). Güç = α (V16) G*Power'da kabul ediliyor: N=2, Actual power=0.0619486; motor bunu eşliyor. Açık soru: spec'te mi eksik (güç < α doğrulaması tanımlı değil), kodda mı hata? | `oracle/screenshots/V17.png`, `oracle/screenshots/V16.png` | Yüksek (gözlem) |

---

## İnceleme Oturumu İçin Açık Sorular

Bu sorular yazım oturumunda **cevaplanmaz**; ayrı inceleme oturumunda binary üzerinde aranacaktır.
Cevap bulunursa ilgili satır adres/dize kanıtıyla `[REA]` olarak eklenir.

| # | Soru | İlgili satır | Ne aranacak |
|---|---|---|---|
| Q1 | 7 ondalık gösterim sabit bir biçim dizesinden mi geliyor, yoksa anlamlı basamak / alan genişliği kuralından mı? Diğer test ailelerinde ve alanlarda da 7 mi? | L11 | Çıktı panelini dolduran kodda sayı biçimlendirme dizesi ya da basamak sayısı sabiti; grafik başlığındaki 5 basamaklı biçimle ilişkisi |
| Q2 | A priori çözücünün durma koşulu Power(N) >= hedef mi? | L06 | N arama döngüsü ve karşılaştırma koşulu |
| Q3 | Çift kuyrukta güç, iki kuyruğun toplamı mı? | L08 | Güç hesabını yapan fonksiyon |
| Q4 | `Power must be greater than or equal to alpha.` doğrulaması hangi modlarda ve hangi karşılaştırmayla (`<` mı, `<=` mı) yapılıyor? | L12 | Bu hata dizesine giden xref ve önündeki karşılaştırma |
