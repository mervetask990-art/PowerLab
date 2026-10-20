# SPEC: t-paired Güç Analizi ve Boyut Belirleme Motoru

Bu belge, `powerlab` kütüphanesinin **t-paired** (eşleştirilmiş iki bağımlı grup ortalaması farkı / matched pairs) ailesi için kabul kriterlerini ve matematiksel davranış şartnamesini tanımlar.

---

## 1. Matematiksel Model ve Formüller

- **Test Ailesi**: `t-paired`
- **Etki Büyüklüğü ($d_z$)**: Fark dağılımının standartlaştırılmış ortalama farkı ($d_z = \frac{\mu_D}{\sigma_D} > 0$).
- **Örneklem Büyüklüğü ($N$)**: Eşleştirilmiş çift sayısı (pairs count). $N \ge 2$.
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
    Then hesaplanan tamsayı N değeri — beklenen: oracle vektörü #V01, G*Power ile doğrulanacak
    And hesaplanan serbestlik derecesi df — beklenen: oracle vektörü #V01, G*Power ile doğrulanacak
    And merkezsizlik parametresi ncp — beklenen: oracle vektörü #V01, G*Power ile doğrulanacak
    And kritik değer critical_t — beklenen: oracle vektörü #V01, G*Power ile doğrulanacak
    And gerçekleşen güç actual_power hedef güçten (0.95) küçük olmamalıdır
    And gerçekleşen güç actual_power değeri — beklenen: oracle vektörü #V01, G*Power ile doğrulanacak

  Scenario: Standart orta etki boyutu ve 0.80 güç (V02)
    Given test ailesi "t-paired"
    And analiz modu "a-priori"
    And kuyruk sayısı 2
    And etki büyüklüğü dz = 0.5
    And alfa anlamlılık düzeyi alpha = 0.05
    And hedeflenen güç power = 0.80
    When a priori güç analizi çözücüsü çalıştırıldığında
    Then hesaplanan tamsayı N değeri — beklenen: oracle vektörü #V02, G*Power ile doğrulanacak
    And hesaplanan serbestlik derecesi df — beklenen: oracle vektörü #V02, G*Power ile doğrulanacak
    And merkezsizlik parametresi ncp — beklenen: oracle vektörü #V02, G*Power ile doğrulanacak
    And gerçekleşen güç actual_power hedef güçten (0.80) küçük olmamalıdır
    And gerçekleşen güç actual_power değeri — beklenen: oracle vektörü #V02, G*Power ile doğrulanacak

  Scenario: Tek kuyruklu a priori analiz (V03)
    Given test ailesi "t-paired"
    And analiz modu "a-priori"
    And kuyruk sayısı 1
    And etki büyüklüğü dz = 0.5
    And alfa anlamlılık düzeyi alpha = 0.05
    And hedeflenen güç power = 0.95
    When a priori güç analizi çözücüsü çalıştırıldığında
    Then hesaplanan tamsayı N değeri — beklenen: oracle vektörü #V03, G*Power ile doğrulanacak
    And hesaplanan serbestlik derecesi df — beklenen: oracle vektörü #V03, G*Power ile doğrulanacak
    And kritik değer critical_t — beklenen: oracle vektörü #V03, G*Power ile doğrulanacak
    And gerçekleşen güç actual_power hedef güçten (0.95) küçük olmamalıdır
    And gerçekleşen güç actual_power değeri — beklenen: oracle vektörü #V03, G*Power ile doğrulanacak

  # -------------------------------------------------------------
  # POST HOC ANALİZLER (Güç Hesaplama)
  # -------------------------------------------------------------
  Scenario: Verilen N için post hoc güç hesabı (V21)
    Given test ailesi "t-paired"
    And analiz modu "post-hoc"
    And kuyruk sayısı 2
    And etki büyüklüğü dz = 0.5
    And alfa anlamlılık düzeyi alpha = 0.05
    And örneklem çift sayısı N = 30
    When post hoc güç analizi çalıştırıldığında
    Then serbestlik derecesi df = 29 olmalıdır
    And merkezsizlik parametresi ncp = 0.5 * sqrt(30) olmalıdır
    And hesaplanan güç değeri G*Power referansıyla tam eşleşmelidir

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
      | tails | dz   | alpha | power | n   | açıklama                     |
      | 2     | -0.5 | 0.05  | 0.80  | -   | Negatif etki büyüklüğü       |
      | 2     | 0.0  | 0.05  | 0.80  | -   | Sıfır etki büyüklüğü         |
      | 2     | 0.5  | 0.00  | 0.80  | -   | Sıfır alfa düzeyi            |
      | 2     | 0.5  | 1.00  | 0.80  | -   | Bire eşit alfa               |
      | 2     | 0.5  | 0.05  | 0.00  | -   | Sıfır hedef güç              |
      | 2     | 0.5  | 0.05  | 1.00  | -   | Bire eşit hedef güç          |
      | 3     | 0.5  | 0.05  | 0.80  | -   | Geçersiz kuyruk sayısı (3)   |
      | 2     | 0.5  | 0.05  | -     | 1   | Post-hoc için df=0 (N=1)     |
      | 2     | 0.5  | 0.05  | -     | -5  | Post-hoc için negatif N      |
