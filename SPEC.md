# SPEC: t-paired Güç Analizi ve Boyut Belirleme Motoru

Bu belge, `powerlab` kütüphanesinin **t-paired** (eşleştirilmiş iki bağımlı grup ortalaması farkı / matched pairs) ailesi için kabul kriterlerini ve matematiksel davranış şartnamesini tanımlar.

---

## 1. Matematiksel Model ve Formüller

- **Test Ailesi**: `t-paired`
- **Etki Büyüklüğü ($d_z$)**: Fark dağılımının standartlaştırılmış ortalama farkı ($d_z = \frac{\mu_D}{\sigma_D}$). **$d_z > 0$ olmalıdır** (CONTRACT.md §5; aksi `OUT_OF_RANGE`).
  - A priori: ayrıca $d_z \ge 0.00001$ olmalıdır; $0 < d_z < 0.00001$ `OUT_OF_RANGE` ([REA] `0x4db990` kesin küçük karşılaştırma, LEDGER L18; $d_z = 0.00001$ kabul, V42).
  - **G*Power davranışı (sözleşme gereği uygulanmaz):** G*Power negatif $d_z$'yi kabul eder, $\delta$ ve critical t'yi işaretli verir, N ve gücü $|d_z|$ ile hesaplar (V21, V26, V37; LEDGER L13); post hoc'ta $d_z = 0$ için güç $= \alpha$ verir (V41, V43; L16). Motor bunları CONTRACT.md §5 gereği reddeder; eğitmene soruldu.
- **Örneklem Büyüklüğü ($N$)**: Eşleştirilmiş çift sayısı (pairs count). A priori çözücü $N \ge 2$ üretir (V16); post hoc girdisi $N \ge 3$ olmalıdır (G*Power V29, V40: izin verilen aralık (3, 2147483646); üst sınır uygulanmaz, LEDGER L15).
- **Hedef Güç**: A priori'de $\text{power} \ge \alpha$ olmalıdır; $\text{power} = \alpha$ kabul (V16), $\text{power} < \alpha$ hata (V17).
- **Serbestlik Derecesi ($\text{df}$)**:
  $$\text{df} = N - 1$$
- **Merkezsizlik Parametresi ($\delta$ / $\text{ncp}$)**:
  $$\delta = d_z \cdot \sqrt{N}$$
- **Dağılım**: Merkezsiz t dağılımı ($T \sim \text{nct}(\text{df}, \delta)$) ve merkezi t dağılımı ($T_0 \sim t(\text{df})$).
- **Kritik Değer ($t_{\text{crit}}$)**:
  - Çift kuyruk (`tails = 2`): $t_{\text{crit}} = t_{1 - \alpha/2, \, \text{df}}$
  - Tek kuyruk (`tails = 1`): $t_{\text{crit}} = t_{1 - \alpha, \, \text{df}}$
- **İstatistiksel Güç ($1 - \beta$)**:
  - Tek kuyruk (`tails = 1`):
    $$\text{Güç} = 1 - F_{\text{nct}}(t_{\text{crit}}; \, \text{df}, \, \delta)$$
  - Çift kuyruk (`tails = 2`):
    $$\text{Güç} = 1 - F_{\text{nct}}(t_{\text{crit}}; \, \text{df}, \, \delta) + F_{\text{nct}}(-t_{\text{crit}}; \, \text{df}, \, \delta)$$
    *(Not: G*Power t testlerinde çift kuyrukta sol kuyruk integralini de dahil eder; etki büyüklüğü orta/büyük olduğunda sol kuyruk $10^{-6}$ mertebesinde ihmal edilebilir olsa da hassas hesaplamada toplanır).*
    *([REA], LEDGER L25, L26: assembly ile doğrulandı. Güç `1 - (F(t_c) - F(-t_c))` biçiminde döner (`0x4d38b0`);
    α'nın ikiye bölünmesi de aynı fonksiyonda kuyruk bayrağına bağlıdır. L22'deki "`0x4bdee0` α'yı böler" okuması
    yanlıştı; orada yarıya bölünen N'dir. δ = dz·√N dönüşümü `0x4dbdc0`'da (L24), df = N − 1 `0x4db950`'de (L28)
    doğrulandı.)*
- **Kritik değerin hesaplanışı ([REA], L28):** Kritik t, merkezsizliği 0 olan (merkezi) t dağılımının ters CDF'idir;
  δ ancak bundan sonra ayarlanıp güç hesaplanır.
- **G*Power'da kuyruk yönü ([REA], L27; sözleşme gereği motorda uygulanmaz):** Yön, etki büyüklüğünün işaretiyle seçilir.
  $d_z \ge 0$ için $t_{\text{crit}}$ üst kuyruktan alınır ($1-\alpha$ ya da $1-\alpha/2$). $d_z < 0$ için alt kuyruktan
  alınır ($\alpha$ ya da $\alpha/2$, negatif $t_{\text{crit}}$); tek kuyruk gücü bu durumda $F_{\text{nct}}(t_{\text{crit}})$ olur.
  $d_z = 0$ üst kuyruk dalına düşer ve güç $= \alpha$ çıkar (V41, V43).
- **Merkezsiz t CDF'i ([REA], L29):** G*Power'da df'e bağlı bir yöntem değişikliği yoktur; aynı seri toplamı her df için
  kullanılır (göreli tolerans ≈ 5.55·10⁻¹⁷, en çok 50000 terim). $|\delta| < 10^{-100}$ ise merkezi t'ye geçilir.
  V42 uyuşmazlığının (L17) nedeni bilinmiyor.
- **G*Power girdi aralıkları ([REA], L32, L33; ekran görüntüsüyle sınanmadı; motor uygular, 818a9d6, aksi `OUT_OF_RANGE`):**
  - $\alpha$ ve hedef güç $[10^{-7},\ 0.9999999]$ kapalı aralığında olmalıdır.
  - Post hoc'ta $d_z \in [-20,\ 20]$ olmalıdır.
  - A priori'de $d_z$ için yalnızca $|d_z| \ge 0.00001$ kontrolü vardır, üst sınır yoktur.
  - A priori kontrol sırası: $d_z$ eşiği → $\alpha$ → güç → $\alpha \le$ güç (motor da bu sırayla denetler).

  Motor bu aralıkları değil CONTRACT.md §5'i uygular; G*Power'ın kabul edip sözleşmenin reddettiği (ya da tersi)
  değerler kasıtlı sapmadır.

---

## 2. A Priori Çözücü Algoritması ve Yuvarlama Davranışı

1. **Arama Aralığı**: $N_{\min} = 2$, **üst sınır yok**. Motor üst ucu 100 000'den başlatır ve güç hedefe ulaşana dek ikiye katlar (V42: N = 78 488 605 096). G*Power aynı amaçla 100'den başlayıp 1.6 ile çarpar ([REA] L34).
2. **Hedef**: İstenen $\text{target\_power} \le \text{actual\_power}$ eşitsizliğini sağlayan **en küçük pozitif tamsayı $N$** değerini bulmak.
3. **Kesikli Arama / Tavan Yuvarlama**:
   - $N$ örneklem çift sayısı kesikli bir tamsayıdır ($N \in \mathbb{N}_{\ge 2}$).
   - $N$ artarken güç monotonik artar.
   - İkili arama (binary search) veya artırımlı tarama ile $\text{Power}(N) \ge \text{target\_power}$ olan en küçük $N$ seçilir.
   - Elde edilen $N$ için `ncp`, `critical_t`, `df`, `n_total`, `actual_power` değerleri raporlanır (CONTRACT.md §4.2).
4. **G*Power'ın gerçek yöntemi ([REA], LEDGER L21)**: G*Power tamsayı tarama yapmaz. Sürekli $N$ üzerinde
   $\text{Power}(N) = \text{target\_power}$ kökünü Brent türü bir kök bulucuyla arar (tolerans $10^{-10}$, en çok 300
   iterasyon), sonucu $\lfloor N \cdot 10^{10} + 0.5 \rfloor / 10^{10}$ ile 10 ondalığa yuvarlar ve tavanını alır
   (`0x496aa0`, `0x4f9bb0`, `0x496a20`). Güç $N$'de monoton olduğu sürece bu, 3. maddedeki "en küçük tamsayı" kuralıyla
   aynı $N$'yi verir; motor 3. maddeyi uygular. İki kuralın ayrışabileceği sınır vakaları (kök bir tamsayıya $10^{-10}$
   içinde yakınsa ya da güç fonksiyonu sayısal olarak farklıysa, bkz. V42 / L17) kâhinle izlenir.
5. **G*Power'ın arama aralığı ([REA], LEDGER L34)**: Kök bulucunun alt sınırı 2'dir; başlangıç noktası 100'dür.
   Güç(100) hedefe ulaşıyorsa aralık 2'ye doğru daraltılır. Ulaşmıyorsa üst uç hedefe ulaşılana dek 1.6 ile çarpılarak
   büyütülür. **G*Power'da üst sınır yoktur** (V42: N = 78488272181). Yuvarlanmış N alt sınırdan küçükse 2'ye çekilir;
   a priori'de en küçük N bu yüzden 2'dir (V16). Güç = α durumunda (V16) aralıkta işaret değişimi olmadığında kök
   bulucunun ne döndürdüğü izlenmedi ([AJAN], L35). *Not: Yukarıdaki 1. maddedeki $N_{\max} = 100\,000$ G*Power
   davranışı değildir; V42 senaryosuyla çelişir.*

---

## 3. Gherkin Kabul Kriterleri (Acceptance Criteria)

### Feature: Eşleştirilmiş t-Testi Güç Analizi (t-paired)

  Kullanıcı veya araştırmacı olarak,
  Eşleştirilmiş iki ölçüm arasındaki ortalama farkı için (örn. tansiyon önce/sonra)
  Gereken örneklem çift sayısını (A priori) veya mevcut örneklemle ulaşılan gücü (Post hoc)
  G*Power 3.1.9.7 ile %100 uyumlu tam sayı N ve basamak doğruluğu ile hesaplamak istiyorum.

  Background:
    Given powerlab hesap motoru hazır durumdadır
    And matematiksel dağılım kütüphanesi noncentral-t fonksiyonunu desteklemektedir

  # -------------------------------------------------------------
  # A PRİORİ ANALİZLER (N Hesaplama)
  # -------------------------------------------------------------
  Scenario: Standart orta etki boyutu ve çift kuyruklu a priori analiz (V01)
    Given test ailesi "t-paired"
    And analiz modu "a-priori"
    And kuyruk sayısı 2
    And etki büyüklüğü dz = 0.5
    And alfa anlamlılık düzeyi alpha = 0.05
    And hedeflenen güç power = 0.95
    When a priori güç analizi çözücüsü çalıştırıldığında
    # Kâhin: oracle vektörü #V01 — G*Power 3.1.9.7 ekranı (oracle/screenshots/V01.png), 7 ondalık
    Then hesaplanan tamsayı N değeri 54 olmalıdır
    And hesaplanan serbestlik derecesi df = 53 olmalıdır
    And merkezsizlik parametresi ncp 7 ondalıkta 3.6742346 olmalıdır
    And kritik değer critical_t 7 ondalıkta 2.0057460 olmalıdır
    And gerçekleşen güç actual_power hedef güçten (0.95) küçük olmamalıdır
    And gerçekleşen güç actual_power 7 ondalıkta 0.9502120 olmalıdır

  Scenario: Standart orta etki boyutu ve 0.80 güç (V03)
    Given test ailesi "t-paired"
    And analiz modu "a-priori"
    And kuyruk sayısı 2
    And etki büyüklüğü dz = 0.5
    And alfa anlamlılık düzeyi alpha = 0.05
    And hedeflenen güç power = 0.80
    When a priori güç analizi çözücüsü çalıştırıldığında
    # Kâhin: oracle vektörü #V03 (oracle/screenshots/V03.png)
    Then hesaplanan tamsayı N değeri 34 olmalıdır
    And hesaplanan serbestlik derecesi df = 33 olmalıdır
    And merkezsizlik parametresi ncp 7 ondalıkta 2.9154759 olmalıdır
    And kritik değer critical_t 7 ondalıkta 2.0345153 olmalıdır
    And gerçekleşen güç actual_power 7 ondalıkta 0.8077775 olmalıdır

  Scenario: Tek kuyruklu a priori analiz (V02)
    Given test ailesi "t-paired"
    And analiz modu "a-priori"
    And kuyruk sayısı 1
    And etki büyüklüğü dz = 0.5
    And alfa anlamlılık düzeyi alpha = 0.05
    And hedeflenen güç power = 0.95
    When a priori güç analizi çözücüsü çalıştırıldığında
    # Kâhin: oracle vektörü #V02 (oracle/screenshots/V02.png)
    Then hesaplanan tamsayı N değeri 45 olmalıdır
    And hesaplanan serbestlik derecesi df = 44 olmalıdır
    And merkezsizlik parametresi ncp 7 ondalıkta 3.3541020 olmalıdır
    And kritik değer critical_t 7 ondalıkta 1.6802300 olmalıdır
    And gerçekleşen güç actual_power 7 ondalıkta 0.9512400 olmalıdır

  Scenario: Hedef güç alfaya eşit kabul edilir (V16)
    Given test ailesi "t-paired"
    And analiz modu "a-priori"
    And kuyruk sayısı 2
    And etki büyüklüğü dz = 0.5
    And alfa anlamlılık düzeyi alpha = 0.05
    And hedeflenen güç power = 0.05
    When a priori güç analizi çözücüsü çalıştırıldığında
    # Kâhin: oracle vektörü #V16 — a priori çözücü N = 2 üretebilir
    Then hesaplanan tamsayı N değeri 2 olmalıdır
    And hesaplanan serbestlik derecesi df = 1 olmalıdır
    And kritik değer critical_t 7 ondalıkta 12.7062047 olmalıdır
    And gerçekleşen güç actual_power 7 ondalıkta 0.0619486 olmalıdır

  Scenario: Mutlak dz alt sınırı 0.00001 a priori'de kabul edilir (V42)
    Given test ailesi "t-paired"
    And analiz modu "a-priori"
    And kuyruk sayısı 2
    And etki büyüklüğü dz = 0.00001
    And alfa anlamlılık düzeyi alpha = 0.05
    And hedeflenen güç power = 0.80
    When a priori güç analizi çözücüsü çalıştırıldığında
    # Kâhin: oracle vektörü #V42. Bilinen uyuşmazlık: motor N = 78488605096 buluyor (LEDGER L17)
    Then motor hata vermemelidir
    And hesaplanan tamsayı N değeri 78488272181 olmalıdır
    And gerçekleşen güç actual_power 7 ondalıkta 0.8000265 olmalıdır

  # -------------------------------------------------------------
  # POST HOC ANALİZLER (Güç Hesaplama)
  # -------------------------------------------------------------
  Scenario: Verilen N için post hoc güç hesabı (V27)
    Given test ailesi "t-paired"
    And analiz modu "post-hoc"
    And kuyruk sayısı 2
    And etki büyüklüğü dz = 0.5
    And alfa anlamlılık düzeyi alpha = 0.05
    And örneklem çift sayısı N = 30
    When post hoc güç analizi çalıştırıldığında
    # Kâhin: oracle vektörü #V27 (oracle/screenshots/V27.png)
    Then serbestlik derecesi df = 29 olmalıdır
    And merkezsizlik parametresi ncp 7 ondalıkta 2.7386128 olmalıdır
    And kritik değer critical_t 7 ondalıkta 2.0452296 olmalıdır
    And hesaplanan güç 7 ondalıkta 0.7539647 olmalıdır

  Scenario Outline: dz <= 0 sözleşme gereği reddedilir; G*Power hesap yapar (kasıtlı sapma)
    Given test ailesi "t-paired"
    And analiz modu "<mode>"
    And kuyruk sayısı <tails>
    And etki büyüklüğü dz = <dz>
    And alfa anlamlılık düzeyi alpha = 0.05
    And <son_girdi>
    When hesaplama çalıştırıldığında
    # CONTRACT.md §5: dz > 0. G*Power'ın kâhin değerleri değişmedi (LEDGER L13, L16); eğitmene soruldu.
    Then hata kodu "OUT_OF_RANGE" ve field "dz" olmalıdır
    And CLI çıkış kodu 2 olmalıdır

    Examples:
      | kâhin | mode     | tails | dz   | son_girdi       | G*Power'ın yaptığı                              |
      | V21   | a-priori | 1     | -0.5 | power = 0.80    | N=27, δ=-2.5980762, critical t=-1.7056179       |
      | V26   | a-priori | 2     | -0.5 | power = 0.80    | N=34, δ=-2.9154759, critical t=-2.0345153       |
      | V37   | post-hoc | 1     | -0.5 | n_total = 30    | power=0.8482542, δ=-2.7386128                    |
      | V41   | post-hoc | 2     | 0    | n_total = 30    | power=0.0500000 (= α), δ=0                       |
      | V43   | post-hoc | 1     | 0    | n_total = 30    | power=0.0500000 (= α), δ=0                       |

  # -------------------------------------------------------------
  # SINIR VE GEÇERSİZ GİRDİ DOĞRULAMALARI
  # -------------------------------------------------------------
  Scenario Outline: Geçersiz parametrelerde kodlu hata (CONTRACT.md §2.4)
    Given test ailesi "t-paired"
    And geçersiz parametre seti: tails=<tails>, dz=<dz>, alpha=<alpha>, power=<power>, n_total=<n_total>
    When hesaplama çağrıldığında
    Then motor `code` = <code> ve `field` = <field> taşıyan bir ValueError fırlatmalıdır
    And CLI stdout'a {"error","code","field"} yazıp çıkış kodu 2 ile dönmelidir

    Examples:
      | tails | dz       | alpha | power | n_total | code         | field   | açıklama                                              |
      | 2     | 0.0      | 0.05  | 0.80  | -       | OUT_OF_RANGE | dz      | A priori sıfır etki büyüklüğü (§5; G*Power V25)       |
      | 2     | -0.5     | 0.05  | 0.80  | -       | OUT_OF_RANGE | dz      | Negatif etki büyüklüğü (§5; G*Power kabul eder, V26)  |
      | 2     | 0.000005 | 0.05  | 0.80  | -       | OUT_OF_RANGE | dz      | A priori 0 < dz < 0.00001 ([REA] L18)                 |
      | 2     | 0.5      | 0.05  | 0.03  | -       | INCONSISTENT | power   | Hedef güç alfadan küçük (G*Power V17, [REA] L19)      |
      | 2     | 0.5      | 0.00  | 0.80  | -       | OUT_OF_RANGE | alpha   | Sıfır alfa düzeyi                                     |
      | 2     | 0.5      | 1.00  | 0.80  | -       | OUT_OF_RANGE | alpha   | Bire eşit alfa                                        |
      | 2     | 0.5      | 0.05  | 0.00  | -       | OUT_OF_RANGE | power   | Sıfır hedef güç                                       |
      | 2     | 0.5      | 0.05  | 1.00  | -       | OUT_OF_RANGE | power   | Bire eşit hedef güç                                   |
      | 3     | 0.5      | 0.05  | 0.80  | -       | OUT_OF_RANGE | tails   | Geçersiz kuyruk sayısı (3)                            |
      | 2     | 0.5      | 0.05  | -     | 2       | OUT_OF_RANGE | n_total | Post hoc N=2 (G*Power V29, [REA] L20)                 |
      | 2     | 0.5      | 0.05  | -     | 1       | OUT_OF_RANGE | n_total | Post hoc N=1 (§5; G*Power V40)                        |
      | 2     | 0.5      | 0.05  | -     | -5      | OUT_OF_RANGE | n_total | Post hoc negatif N                                    |
      | 2     | 0.5      | 0.05  | -     | 30.5    | INVALID_VALUE| n_total | Tam sayı olması gereken yerde ondalık                 |
      | 2     | 0.5      | 1e-8  | 0.80  | -       | OUT_OF_RANGE | alpha   | α < 1e-7 ([REA] L32)                                  |
      | 2     | 0.5      | 0.05  | 0.99999999 | -  | OUT_OF_RANGE | power   | Güç > 0.9999999 ([REA] L32)                           |
      | 2     | 20.5     | 0.05  | -     | 30      | OUT_OF_RANGE | dz      | Post hoc dz > 20 ([REA] L33)                          |


  # -------------------------------------------------------------
  # BONUS MODLAR (CONTRACT.md §3) — kâhin: oracle/gpower_bonus_modes.csv (K01–K09)
  # -------------------------------------------------------------
  Scenario: Compromise analizinde α ve β, β/α oranına göre birlikte seçilir (K01)
    Given test ailesi "t-paired" ve analiz modu "compromise"
    And kuyruk sayısı 2, dz = 0.5, β/α oranı = 1, N = 54
    When analiz çalıştırıldığında
    Then df = 53 olmalıdır
    And δ 7 ondalıkta 3.6742346, kritik t 7 ondalıkta 2.0067386 olmalıdır
    And α ve β 7 ondalıkta 0.0498908, güç 7 ondalıkta 0.9501092 olmalıdır

  Scenario: Criterion analizi gücü sağlayan α'yı bulur (K04)
    Given test ailesi "t-paired" ve analiz modu "criterion"
    And kuyruk sayısı 2, dz = 0.5, güç = 0.95, N = 54
    When analiz çalıştırıldığında
    Then df = 53 olmalıdır
    And kritik t 7 ondalıkta 2.0077915, α 7 ondalıkta 0.0497751 olmalıdır

  Scenario: Sensitivity analizi saptanabilecek en küçük dz'yi bulur (K07)
    Given test ailesi "t-paired" ve analiz modu "sensitivity"
    And kuyruk sayısı 2, α = 0.05, güç = 0.95, N = 54
    When analiz çalıştırıldığında
    Then df = 53 olmalıdır
    And δ 7 ondalıkta 3.6721359, dz 7 ondalıkta 0.4997144 olmalıdır

  Scenario Outline: Bonus modlarda geçersiz girdi
    Given test ailesi "t-paired" ve analiz modu "<mod>"
    And girdi: <girdi>
    When analiz çalıştırıldığında
    Then hata kodu "<kod>" ve alan "<alan>" olmalıdır

    Examples:
      | mod         | girdi                          | kod           | alan             |
      | compromise  | β/α oranı = 0                   | OUT_OF_RANGE  | beta_alpha_ratio |
      | compromise  | N = 2 ([REA] L20)               | OUT_OF_RANGE  | n_total          |
      | compromise  | --power verildi (ilgisiz alan)  | UNKNOWN_PARAM | power            |
      | sensitivity | güç = 0.03 < α ([REA] L19)      | INCONSISTENT  | power            |

---

## 4. Arayüz (CONTRACT.md 1.0.0)

- **Komut:** `gpower-clone --test t-paired --mode <a-priori|post-hoc> --tails <1|2> --dz <d> --alpha <α> (--power <1-β> | --n_total <N>)`.
  Alan adları birebir; takma ad ve varsayılan değer yoktur (`--tails` zorunlu). `gpower-clone --version` sözleşme sürümünü yazar.
- **Çıktı (stdout, tek satır JSON, tam double, yuvarlama yok):**
  - a-priori: `ncp`, `critical_t`, `df`, `n_total`, `actual_power`
  - post-hoc: `ncp`, `critical_t`, `df`, `power`
  - compromise (girdi `--beta_alpha_ratio`, `--n_total`): `ncp`, `critical_t`, `df`, `alpha`, `beta`, `power`
  - criterion (girdi `--power`, `--n_total`): `ncp`, `critical_t`, `df`, `alpha`
  - sensitivity (girdi `--alpha`, `--power`, `--n_total`): `ncp`, `critical_t`, `df`, `dz`
- **Hata:** `{"error","code","field"}`; kodlar `MISSING_PARAM`, `UNKNOWN_PARAM` (tanınmayan ya da modla ilgisiz alan),
  `INVALID_VALUE`, `OUT_OF_RANGE`, `INCONSISTENT`, `UNSUPPORTED` (bilinmeyen ya da uygulanmamış test/mod).
  Çıkış kodu 2 geçersiz girdi, 1 iç hata. Öncelik: test/mode eksik → desteklenmiyor → tanınmayan alan → eksik alan
  → değer biçimi → aralık → tutarlılık.
- **MCP:** `power_analysis` aracı aynı alan adlarını kullanır; metin içeriği CLI stdout'u ile birebir aynıdır
  (25 referans vektöründe eşdeğerlik testi, `tests/test_mcp_equivalence.py`).
- **Süre:** her çağrı < 2 s (`tests/test_timing.py`); motor `scipy.stats` yerine `scipy.special` kullanır.
