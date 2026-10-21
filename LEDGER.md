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
| L07 | [AJAN] | Sınır | dz <= 0 veya alpha <= 0 veya alpha >= 1 için GUI hesaplamayı reddeder ya da hata kutusu açar. | G*Power arayüz doğrulama davranış hipotezi. **KISMEN ÇÜRÜTÜLDÜ:** a priori'de dz = 0 reddi doğrulandı (V25, L14); negatif dz reddi çürütüldü (V21, V26, L13); post hoc'ta dz = 0 da kabul ediliyor (V41, V43, L16). alpha sınırları kâhinle sınanmadı. | Yüksek (%90) |
| L08 | [AJAN] | Dağılım | Çift kuyrukta güç hesabının iki taraflı noncentral t kuyruğunu topladığı varsayılır: (1 - cdf(t_crit)) + cdf(-t_crit). Not: sol kuyruğun NaN dönmesi G*Power davranışı değil, scipy'ye özgü bir sayısal sorundur (motor 0.0 kabul eder). | Adres/dize yok; yalnızca scipy denemesi. (kanıt bekleniyor: Ghidra) | Orta |
| L09 | [DOK] | Fark | statsmodels.stats.power.ttest_power kesirli N verir; G*Power her zaman tamsayı N verir ve actual_power'ı bu tamsayı N ile günceller. | Faul et al. (2007) | Yüksek |
| L10 | [KÂHİN] | Çözücü | V01 (t-paired, a-priori, iki kuyruk, dz=0.5, α=0.05, güç=0.95): G*Power N=54, Df=53, δ=3.6742346, Critical t=2.0057460, Actual power=0.9502120 gösteriyor. Motor 7 basamakta beş değerin hepsini aynı üretiyor. | `oracle/screenshots/V01.png` | Yüksek (gözlem) |
| L11 | [KÂHİN] | Biçim | KÂHİN GÖZLEMİ: G*Power çıktıyı 7 ondalık basamakla gösterir (Output Parameters paneli; δ, Critical t, Actual power). Grafik başlığı ise `critical t = 2.00575` biçiminde 5 basamak gösteriyor. | `oracle/screenshots/V01.png` | Yüksek (gözlem) |
| L12 | [KÂHİN] | Sınır | KÂHİN GÖZLEMİ / UYUŞMAZLIK: V17 (a-priori, iki kuyruk, dz=0.5, α=0.05, güç=0.03): G*Power "Input error" kutusu açıyor: `Power must be greater than or equal to alpha.`; çıktı alanları `?`. Motor ise hata vermeden N=2 döndürüyor (V16 ile aynı çıktı). Güç = α (V16) G*Power'da kabul ediliyor: N=2, Actual power=0.0619486; motor bunu eşliyor. Açık soru: spec'te mi eksik (güç < α doğrulaması tanımlı değil), kodda mı hata? **Motor uyarlandı (18b9011):** güç < α hata, güç = α kabul. | `oracle/screenshots/V17.png`, `oracle/screenshots/V16.png` | Yüksek (gözlem) |
| L13 | [KÂHİN] | Sınır | KÂHİN GÖZLEMİ / UYUŞMAZLIK: G*Power negatif dz'yi reddetmiyor, hesap yapıyor. V21 (a-priori, tek kuyruk, dz=-0.5, α=0.05, güç=0.80): N=27, Df=26, δ=-2.5980762, Critical t=-1.7056179, Actual power=0.8118316. V26 (iki kuyruk, dz=-0.5): N=34, Df=33, δ=-2.9154759, Critical t=-2.0345153, Actual power=0.8077775. N, Df ve Actual power pozitif eşleri V04/V03 ile aynı; δ ve Critical t işaret değiştiriyor (tek kuyrukta test sola dönüyor). Motor ise ikisinde de `ValueError` (dz > 0 olmalı) veriyor. boundary B06 'error' bekliyor; bu kâhinle çelişiyor. Açık soru: spec'te mi eksik, kodda mı hata? **Motor uyarlandı (18b9011):** N ve güç \|dz\| ile, δ ve critical işaretli. | `oracle/screenshots/V21.png`, `oracle/screenshots/V26.png` | Yüksek (gözlem) |
| L14 | [KÂHİN] | Sınır | KÂHİN GÖZLEMİ: V25 (a-priori, iki kuyruk, dz=0): G*Power "Input error" kutusu açıyor: `In an a priori analysis, the absolute value of the effect size be greater than 0.00001.` (metin aynen, "must" yok); çıktı alanları `?`. Motor da dz=0'ı reddediyor (tepki uyumlu). Ancak mesaj eşiğin 0 değil \|dz\| > 0.00001 olduğunu söylüyor: motor dz=0.000005 için hata vermeden N=313954420375 döndürüyor (motor çıktısı, kâhin değil; G*Power'ın bu girdideki tepkisi ekranla doğrulanmadı). V42 (a-priori, iki kuyruk, dz=0.00001, α=0.05, güç=0.80): G*Power hata vermeden N=78488272181 veriyor; yani 0.00001 sınır değeri kabul ediliyor, mesajdaki "greater than" ifadesi bu değerde davranışla örtüşmüyor. **Motor uyarlandı (18b9011):** a priori'de \|dz\| < 0.00001 hata. 0 < \|dz\| < 0.00001 reddi doğrulanmamış hipotez (Q5, boundary B19). | `oracle/screenshots/V25.png` | Yüksek (gözlem) |
| L15 | [KÂHİN] | Sınır | KÂHİN GÖZLEMİ / UYUŞMAZLIK: Post hoc'ta G*Power N=2 (V29) ve N=1 (V40) için "Input error" kutusu açıyor: `Total sample size is outside the admissible range (3, 2147483646)`; çıktı alanları `?`. Motor N=1'i reddediyor (uyumlu), N=2'de ise hata vermeden sonuç döndürüyor (Df=1, power=0.0619486). Not: a priori V16'da G*Power'ın kendisi N=2 çıktısı veriyor; yani alt sınır 3 yalnızca post hoc girdi doğrulamasında görülüyor. Açık soru: spec'te mi eksik, kodda mı hata? Üst sınır 2147483646 yalnızca post hoc girdisinde görülüyor: a priori V42'de G*Power'ın kendi çıktısı N=78488272181 bu sınırı aşıyor. Üst sınır motora **uygulanmadı** (kullanıcı kararı). **Motor uyarlandı (18b9011):** post hoc N < 3 hata; a priori çözücü N = 2 üretebilir. | `oracle/screenshots/V29.png`, `oracle/screenshots/V40.png`, `oracle/screenshots/V16.png` | Yüksek (gözlem) |
| L16 | [KÂHİN] | Sınır | KÂHİN GÖZLEMİ / UYUŞMAZLIK: Post hoc'ta G*Power dz ≤ 0'ı reddetmiyor. V41 (iki kuyruk, dz=0, α=0.05, N=30): δ=`0` (panelde ondalıksız), Critical t=2.0452296, Df=29, Power=0.0500000 (= α). V37 (tek kuyruk, dz=-0.5, N=30): δ=-2.7386128, Critical t=-1.6991270, Df=29, Power=0.8482542 (V28'in işaret değiştirmiş hali; L13 ile tutarlı). Motor ikisinde de `ValueError` (dz > 0 olmalı) veriyor. dz=0 reddi yalnızca a priori'de (L14 mesajı "In an a priori analysis" diye başlıyor). V43 (tek kuyruk, dz=0, N=30): δ=`0`, Critical t=1.6991270, Df=29, Power=0.0500000; tek kuyrukta da güç = α. **Motor uyarlandı (18b9011):** post hoc'ta her sonlu dz kabul. | `oracle/screenshots/V41.png`, `oracle/screenshots/V37.png` | Yüksek (gözlem) |
| L17 | [KÂHİN] | Sayısal | KÂHİN GÖZLEMİ / UYUŞMAZLIK: V42 (a-priori, iki kuyruk, dz=0.00001, α=0.05, güç=0.80): G*Power N=78488272181, Df=78488272180, δ=2.8015758, Critical t=1.9599640, Actual power=0.8000265 gösteriyor. Motor N=78488605096 buluyor (fark ≈ 333 bin, göreli ≈ 4·10⁻⁶). Motor çıktısı (kâhin değil): G*Power'ın N'sinde scipy gücü 0.7999983 hesaplıyor, yani hedefin altında; G*Power aynı N'de 0.8000265 gösteriyor. Fark çok büyük df'de güç hesabının sayısal yönteminden geliyor görünüyor. Kâhin değeri değiştirilmedi; motor bu commit dizisinde bu konuda değiştirilmedi. Açık soru: G*Power çok büyük df'de noncentral t yerine bir yaklaşım mı kullanıyor? | `oracle/screenshots/V42.png` | Yüksek (gözlem) |

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
| Q5 | Negatif dz'de işaret nasıl işleniyor (tek kuyrukta yön \|dz\| ile mi, işaretle mi seçiliyor)? dz=0.00001 kabul ediliyor (V42), dz=0 reddediliyor (V25): 0 ile 0.00001 arasındaki eşik ve karşılaştırma (`<` mı, `<=` mı) ne? Bu kural a priori dışında da geçerli mi? | L13, L14 | `effect size be greater than 0.00001` dizesine giden xref; dz'nin mutlak değerinin alındığı yer |
| Q6 | Post hoc N alt sınırı 3 neden (df ≥ 2)? A priori çözücü N=2 üretebildiğine göre (V16) iki yol farklı sınır mı kullanıyor? | L15 | `outside the admissible range` dizesine giden xref; aralık sabitleri |
| Q7 | Çok büyük df'de (≈ 7.8·10¹⁰) güç hangi yöntemle hesaplanıyor (normal yaklaşım, seri açılımı, farklı nct algoritması)? | L17 | Güç fonksiyonunda df'e bağlı dallanma; noncentral t CDF uygulaması |
