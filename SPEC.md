# SPEC: t-paired Güç Analizi ve Boyut Belirleme Motoru

Bu belge, `powerlab` kütüphanesinin **t-paired** (eşleştirilmiş iki bağımlı grup ortalaması farkı / matched pairs) ailesi için kabul kriterlerini ve matematiksel davranış şartnamesini tanımlar.

---

## 1. Matematiksel Model ve Formüller

- **Test Ailesi**: `t-paired`
- **Etki Büyüklüğü ($d_z$)**: Fark dağılımının standartlaştırılmış ortalama farkı ($d_z = \frac{\mu_D}{\sigma_D}$). **İşaretlidir.**
  - A priori: $|d_z| \ge 0.00001$ olmalıdır; $d_z = 0$ hata (G*Power V25), $d_z = 0.00001$ kabul (V42). $0 < |d_z| < 0.00001$ aralığının reddi doğrulanmamış hipotezdir (LEDGER Q5).
  - Post hoc: her sonlu $d_z$ kabul edilir; $d_z = 0$ için güç $= \alpha$ (V41, V43).
- **Örneklem Büyüklüğü ($N$)**: Eşleştirilmiş çift sayısı (pairs count). A priori çözücü $N \ge 2$ üretir (V16); post hoc girdisi $N \ge 3$ olmalıdır (G*Power V29, V40: izin verilen aralık (3, 2147483646); üst sınır uygulanmaz, LEDGER L15).
- **Hedef Güç**: A priori'de $\text{power} \ge \alpha$ olmalıdır; $\text{power} = \alpha$ kabul (V16), $\text{power} < \alpha$ hata (V17).
- **Serbestlik Derecesi ($\text{df}$)**:
  $$\text{df} = N - 1$$
- **Merkezsizlik Parametresi ($\delta$ / $\text{ncp}$)**:
  $$\delta = d_z \cdot \sqrt{N}$$
  - $\delta$ işaretli raporlanır. Güç ve N, $|d_z|$ ile hesaplanır (işaret testin yönünü belirler; V21, V26, V37).
- **Dağılım**: Merkezsiz t dağılımı ($T \sim \text{nct}(\text{df}, \delta)$) ve merkezi t dağılımı ($T_0 \sim t(\text{df})$).
- **Kritik Değer ($t_{\text{crit}}$)**:
  - Çift kuyruk (`tails = 2`): $t_{\text{crit}} = t_{1 - \alpha/2, \, \text{df}}$
  - Tek kuyruk (`tails = 1`): $t_{\text{crit}} = t_{1 - \alpha, \, \text{df}}$
  - Raporlanan `critical`, $d_z$'nin işaretini taşır ($d_z < 0$ ise $-t_{\text{crit}}$, $d_z = 0$ ise $+t_{\text{crit}}$).
- **İstatistiksel Güç ($1 - \beta$)** (aşağıda $\delta$ yerine $|\delta|$ kullanılır):
  - Tek kuyruk (`tails = 1`):
    $$\text{Güç} = 1 - F_{\text{nct}}(t_{\text{crit}}; \, \text{df}, \, \delta)$$
  - Çift kuyruk (`tails = 2`):
    $$\text{Güç} = 1 - F_{\text{nct}}(t_{\text{crit}}; \, \text{df}, \, \delta) + F_{\text{nct}}(-t_{\text{crit}}; \, \text{df}, \, \delta)$$
    *(Not: G*Power t testlerinde çift kuyrukta sol kuyruk integralini de dahil eder; etki büyüklüğü orta/büyük olduğunda sol kuyruk $10^{-6}$ mertebesinde ihmal edilebilir olsa da hassas hesaplamada toplanır).*

---

## 2. A Priori Çözücü Algoritması ve Yuvarlama Davranışı

1. **Arama Aralığı**: $N_{\min} = 2$, $N_{\max} = 100\,000$.
2. **Hedef**: İstenen $\text{target\_power} \le \text{actual\_power}$ eşitsizliğini sağlayan **en küçük pozitif tamsayı $N$** değerini bulmak.
3. **Kesikli Arama / Tavan Yuvarlama**:
   - $N$ örneklem çift sayısı kesikli bir tamsayıdır ($N \in \mathbb{N}_{\ge 2}$).
   - $N$ artarken güç monotonik artar.
   - İkili arama (binary search) veya artırımlı tarama ile $\text{Power}(N) \ge \text{target\_power}$ olan en küçük $N$ seçilir.
   - Elde edilen $N$ için `actual_power`, `critical`, `df`, `ncp` değerleri raporlanır.

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

  Scenario: Negatif etki büyüklüğü, çift kuyruk a priori (V26)
    Given test ailesi "t-paired"
    And analiz modu "a-priori"
    And kuyruk sayısı 2
    And etki büyüklüğü dz = -0.5
    And alfa anlamlılık düzeyi alpha = 0.05
    And hedeflenen güç power = 0.80
    When a priori güç analizi çözücüsü çalıştırıldığında
    # Kâhin: oracle vektörü #V26 — N, df ve güç pozitif eşi V03 ile aynı; δ ve critical işaretli
    Then hesaplanan tamsayı N değeri 34 olmalıdır
    And hesaplanan serbestlik derecesi df = 33 olmalıdır
    And merkezsizlik parametresi ncp 7 ondalıkta -2.9154759 olmalıdır
    And kritik değer critical_t 7 ondalıkta -2.0345153 olmalıdır
    And gerçekleşen güç actual_power 7 ondalıkta 0.8077775 olmalıdır

  Scenario: Negatif etki büyüklüğü, tek kuyruk a priori (V21)
    Given test ailesi "t-paired"
    And analiz modu "a-priori"
    And kuyruk sayısı 1
    And etki büyüklüğü dz = -0.5
    And alfa anlamlılık düzeyi alpha = 0.05
    And hedeflenen güç power = 0.80
    When a priori güç analizi çözücüsü çalıştırıldığında
    # Kâhin: oracle vektörü #V21 — pozitif eşi V04
    Then hesaplanan tamsayı N değeri 27 olmalıdır
    And hesaplanan serbestlik derecesi df = 26 olmalıdır
    And merkezsizlik parametresi ncp 7 ondalıkta -2.5980762 olmalıdır
    And kritik değer critical_t 7 ondalıkta -1.7056179 olmalıdır
    And gerçekleşen güç actual_power 7 ondalıkta 0.8118316 olmalıdır

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

  Scenario: Negatif etki büyüklüğü, tek kuyruk post hoc (V37)
    Given test ailesi "t-paired"
    And analiz modu "post-hoc"
    And kuyruk sayısı 1
    And etki büyüklüğü dz = -0.5
    And alfa anlamlılık düzeyi alpha = 0.05
    And örneklem çift sayısı N = 30
    When post hoc güç analizi çalıştırıldığında
    # Kâhin: oracle vektörü #V37 — pozitif eşi V28
    Then merkezsizlik parametresi ncp 7 ondalıkta -2.7386128 olmalıdır
    And kritik değer critical_t 7 ondalıkta -1.6991270 olmalıdır
    And hesaplanan güç 7 ondalıkta 0.8482542 olmalıdır

  Scenario Outline: Post hoc dz = 0 kabul edilir, güç alfaya eşittir (V41, V43)
    Given test ailesi "t-paired"
    And analiz modu "post-hoc"
    And kuyruk sayısı <tails>
    And etki büyüklüğü dz = 0
    And alfa anlamlılık düzeyi alpha = 0.05
    And örneklem çift sayısı N = 30
    When post hoc güç analizi çalıştırıldığında
    Then merkezsizlik parametresi ncp 0 olmalıdır
    And kritik değer critical_t 7 ondalıkta <critical> olmalıdır
    And hesaplanan güç 7 ondalıkta 0.0500000 olmalıdır

    Examples:
      | tails | critical  | kâhin |
      | 2     | 2.0452296 | V41   |
      | 1     | 1.6991270 | V43   |

  # -------------------------------------------------------------
  # SINIR VE GEÇERSİZ GİRDİ DOĞRULAMALARI
  # -------------------------------------------------------------
  Scenario Outline: Geçersiz parametrelerde açıklayıcı ValueError üretimi
    Given test ailesi "t-paired"
    And geçersiz parametre seti: tails=<tails>, dz=<dz>, alpha=<alpha>, power=<power>, n=<n>
    When hesaplama fonksiyonu çağrıldığında
    Then motor "ValueError" fırlatmalıdır
    And CLI sıfırdan farklı bir çıkış kodu ile JSON error mesajı dönmelidir

    Examples:
      | tails | dz       | alpha | power | n   | açıklama                                                     |
      | 2     | 0.0      | 0.05  | 0.80  | -   | A priori sıfır etki büyüklüğü (G*Power V25)                  |
      | 2     | 0.000005 | 0.05  | 0.80  | -   | A priori 0 < mutlak dz < 0.00001 (doğrulanmamış hipotez, Q5) |
      | 2     | 0.5      | 0.05  | 0.03  | -   | Hedef güç alfadan küçük (G*Power V17)                        |
      | 2     | 0.5      | 0.00  | 0.80  | -   | Sıfır alfa düzeyi                                            |
      | 2     | 0.5      | 1.00  | 0.80  | -   | Bire eşit alfa                                               |
      | 2     | 0.5      | 0.05  | 0.00  | -   | Sıfır hedef güç                                              |
      | 2     | 0.5      | 0.05  | 1.00  | -   | Bire eşit hedef güç                                          |
      | 3     | 0.5      | 0.05  | 0.80  | -   | Geçersiz kuyruk sayısı (3)                                   |
      | 2     | 0.5      | 0.05  | -     | 2   | Post hoc N=2 (G*Power V29: aralık 3–2147483646)              |
      | 2     | 0.5      | 0.05  | -     | 1   | Post hoc N=1 (G*Power V40)                                   |
      | 2     | 0.5      | 0.05  | -     | -5  | Post hoc negatif N                                           |
