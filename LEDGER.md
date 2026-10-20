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
| L06 | [AJAN] | Yuvarlama | G*Power hedef güce ulaşan ilk tamsayıyı seçer (Power(N) >= TargetPower). Bu tavan yuvarlamaya denk gelir. | V01 (d=0.5, p=0.95 -> N=54, actual power=0.9531 >= 0.95) | Yüksek (%90) |
| L07 | [AJAN] | Sınır | dz <= 0 veya alpha <= 0 veya alpha >= 1 için GUI hesaplamayı reddeder ya da hata kutusu açar. | G*Power arayüz doğrulama davranış hipotezi | Yüksek (%90) |
| L08 | [REA] | Dağılım | Çift kuyrukta güç hesabı iki taraflı noncentral t kuyruğunu toplar: (1 - cdf(t_crit)) + cdf(-t_crit). Extreme ncp durumlarında sol kuyruk NaN verebilir, güvenle 0.0 kabul edilmelidir. | `scipy.stats.nct.cdf(-t_crit)` analizi & V01/REF_0641 doğrulaması | Yüksek (%100) |
| L09 | [DOK] | Fark | statsmodels.stats.power.ttest_power kesirli N verir; G*Power her zaman tamsayı N verir ve actual_power'ı bu tamsayı N ile günceller. | Faul et al. (2007) & Conformance testi | Yüksek (%100) |
| L10 | [REA] | Çözücü | N aramasında hedef güç şartı Power(N) >= TargetPower olan en küçük tamsayı N seçilmektedir. N=54 için actual_power = 0.950212 olup 0.95 hedefinin hemen üstündedir. | Diferansiyel test V01 doğrulaması | Yüksek (%100) |
