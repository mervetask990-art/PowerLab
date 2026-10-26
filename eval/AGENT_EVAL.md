# Ajan değerlendirmesi

Model: `gemini-3.5-flash-lite` (Gemini; sınıflandırıcı ve ajan aynı model). Set: `eval/agent_eval.jsonl` (10 kurgusal
soru, Türkçe ve İngilizce). Beklenen aile, parametreler ve N / güç her soru için setin içindedir; beklenen
değerler G*Power ekran görüntülerinden ya da CONTRACT.md §9'dan gelir (`tests/test_agent_eval_set.py`
denetler). Ham sonuçlar: `eval/results/`. Yeniden üretim: `python eval/run_agent_eval.py`,
`python eval/run_gui_comparison.py`, `python eval/generate_eval_report.py`.

**Sistem 1 (test ailesi seçimi):** Jev erişimi olmadığı için yönergedeki izinle aynı etiket setine
(`t2-indep`, `t-paired`, `anova-oneway`, `chi2-contingency`, `multireg-r2`, `ambiguous`, `unsupported`)
JSON şemasıyla kısıtlanmış Gemini kullanıldı (`src/powerlab/agent/classifier.py`). Sınıflandırıcı sayı
üretmez. Güven 0.75'in altındaysa ya da etiket `ambiguous` / `unsupported` ise karar araştırmacıya sorulur.

## Sonuçlar

### Türkçe

| Soru | Beklenen aile | Seçilen (güven) | Aile doğru | Araca giden çağrı | Sonuç doğru | Token (giriş+çıkış) | Süre |
|---|---|---|---|---|---|---|---|
| E01 | t-paired | t-paired (0.99) | ✅ | a-priori → n_total=45, actual_power=0.9512400452506585 | ✅ | 2497+144 | 6.53 s |
| E02 | t-paired | t-paired (0.99) | ✅ | a-priori → n_total=34, actual_power=0.807777501279274 | ✅ | 2481+173 | 7.02 s |
| E03 | t-paired | t-paired (0.99) | ✅ | post-hoc → power=0.7539647157437903 | ✅ | 2485+205 | 5.58 s |
| E04 | multireg-r2 | multireg-r2 (0.99) | ✅ | a-priori → n_total=92, actual_power=0.8041921362300529 | ✅ | 2558+121 | 6.22 s |
| E05 | multireg-r2 | multireg-r2 (0.99) | ✅ | post-hoc → power=0.8429602940479357 | ✅ | 2497+222 | 3.48 s |
| E06 | t-paired | t-paired (1.00) | ✅ | a-priori → n_total=199, actual_power=0.8016910240370654 | ✅ | 4952+242 | 7.96 s |
| E07 | t2-indep | t2-indep (1.00) | ✅ | yok | ✅ | 324+24 | 1.22 s |
| E08 | anova-oneway | anova-oneway (1.00) | ✅ | yok | ✅ | 317+23 | 1.02 s |
| E09 | ambiguous | ambiguous (0.95) | ✅ | yok | ✅ | 276+16 | 1.5 s |
| E10 | unsupported | unsupported (0.99) | ✅ | yok | ✅ | 298+22 | 0.9 s |

### İngilizce

| Soru | Beklenen aile | Seçilen (güven) | Aile doğru | Araca giden çağrı | Sonuç doğru | Token (giriş+çıkış) | Süre |
|---|---|---|---|---|---|---|---|
| E01 | t-paired | t-paired (0.99) | ✅ | a-priori → n_total=45, actual_power=0.9512400452506585 | ✅ | 2491+148 | 2.68 s |
| E02 | t-paired | t-paired (0.99) | ✅ | a-priori → n_total=34, actual_power=0.807777501279274 | ✅ | 2481+159 | 3.18 s |
| E03 | t-paired | t-paired (0.99) | ✅ | post-hoc → power=0.7539647157437903 | ✅ | 2482+209 | 7.25 s |
| E04 | multireg-r2 | multireg-r2 (0.99) | ✅ | a-priori → n_total=92, actual_power=0.8041921362300529 | ✅ | 2528+190 | 4.15 s |
| E05 | multireg-r2 | multireg-r2 (1.00) | ✅ | post-hoc → power=0.8429602940479357 | ✅ | 2479+192 | 4.47 s |
| E06 | t-paired | t-paired (0.99) | ✅ | a-priori → n_total=199, actual_power=0.8016910240370654 | ✅ | 4925+223 | 4.06 s |
| E07 | t2-indep | t2-indep (1.00) | ✅ | yok | ✅ | 321+24 | 0.75 s |
| E08 | anova-oneway | anova-oneway (1.00) | ✅ | yok | ✅ | 313+23 | 1.77 s |
| E09 | ambiguous | ambiguous (0.95) | ✅ | yok | ✅ | 279+22 | 1.08 s |
| E10 | unsupported | unsupported (0.99) | ✅ | yok | ✅ | 293+22 | 1.79 s |

## Özet: doğru seçim oranı ve Türkçe–İngilizce karşılaştırması

| Ölçüt | Türkçe | İngilizce |
|---|---|---|
| Test ailesi doğru seçildi | 10/10 (%100) | 10/10 (%100) |
| Uçtan uca doğru davranış (doğru hesap ya da doğru şekilde hesap yapmama) | 10/10 (%100) | 10/10 (%100) |
| Ortalama güven | 0.99 | 0.99 |
| Toplam token (giriş+çıkış) | 18685+1192 | 18592+1212 |
| Toplam süre | 41.4 s | 31.2 s |

## Kalibrasyon

Sınıflandırıcının söylediği güven ile gerçek doğruluk (iki dil birlikte, 20 seçim):

| Güven aralığı | Seçim sayısı | Ortalama güven | Gerçekte doğru |
|---|---|---|---|
| 0.90–1.00 | 20 | 0.99 | 20/20 (%100) |
| 0.75–0.89 | 0 | — | — |
| < 0.75 | 0 | — | — |

Örneklem çok küçük (20 seçim); bu tablo kalibrasyon hakkında yalnızca kaba bir fikir verir.

## Token karşılaştırması: MCP yolu ve GUI yolu

Hesap gerektiren sorular (E01–E06, Türkçe). MCP yolu: sınıflandırıcı + ajan + MCP aracı, metin.
GUI yolu: aynı soru, G*Power'ın sonucu gösteren ekran görüntüsüyle (`eval/run_gui_comparison.py`).

| Soru | MCP token | MCP süre | MCP doğru | GUI token | GUI süre | GUI doğru | GUI / MCP token |
|---|---|---|---|---|---|---|---|
| E01 | 2641 | 6.53 s | ✅ | 1245 | 2.01 s | ✅ | 0.47 |
| E02 | 2654 | 7.02 s | ✅ | 1240 | 2.02 s | ✅ | 0.47 |
| E03 | 2690 | 5.58 s | ✅ | 1256 | 1.39 s | ✅ | 0.47 |
| E04 | 2679 | 6.22 s | ✅ | 1257 | 1.51 s | ✅ | 0.47 |
| E05 | 2719 | 3.48 s | ✅ | 1287 | 1.62 s | ✅ | 0.47 |
| E06 | 5194 | 7.96 s | ✅ | 1297 | 2.05 s | ✅ | 0.25 |
| **Toplam** | **18577** | **36.8 s** | **6/6** | **7582** | **10.6 s** | **6/6** | **0.41** |

**Bulgu (ölçülen):** Bu ölçümde MCP yolu, tek ekran görüntüsü okumaktan **daha pahalı** çıktı (GUI / MCP = 0.41). Ekran görüntüsü başına ortalama 1264 token ölçüldü; MCP yolunun maliyetine soru başına yaklaşık **2.5 ekran görüntüsünde** ulaşılır. Yönergedeki "bir ekran görüntüsü yüzlerce, hatta binlerce token" tahmini doğrulandı (~1.3 bin). Ama metin yolu "birkaç token" değil: araç çağrısının kendisi (JSON girdi ve çıktı) kısadır, ajan döngüsünün tokenlarının çoğu ise her turda yeniden gönderilen sistem talimatı ve araç şemasıdır; soru başına iki model turu ve bir sınıflandırıcı çağrısı vardır. CLI'yi doğrudan çağıran bir ajan bu sabit maliyeti ödemez.

**Tahmin (ölçülmedi):** G*Power'da bir hesap en az üç ekran gerektirir (test ailesi seçimi, girdilerin girilmesi, sonuç); her tıklamadan sonra görüntü alan bir GUI ajanı için bu sayı daha yüksektir. Üç görüntüde GUI yolu yaklaşık 3791 token olur ve MCP yolunu geçer. Bu bir tahmindir; gerçek bir GUI ajanı bu projede çalıştırılmadı.

**Yorum ve sınırlar:**
- GUI satırı GUI yolunun **alt sınırıdır**: yalnızca sonucu gösteren tek bir ekran görüntüsünün okunması
  ölçüldü. Gerçek bir GUI ajanı test ailesini seçmek, her alanı doldurmak ve "Calculate"e basmak için her
  adımda yeni bir ekran görüntüsü alır; toplam maliyet bu tablodakinin birkaç katı olur.
- MCP satırı ise üst sınıra yakındır: sınıflandırıcı çağrısını, araç şemasını taşıyan sistem talimatını ve
  modelin cevabı yazdığı turu da içerir.
- GUI yolunda doğru değer, ancak birisi G*Power'a girdileri doğru girdiyse ekranda vardır; okuma doğruluğu
  hesabın doğruluğunu göstermez. MCP yolunda değer motordan gelir ve G*Power'a karşı ayrıca test edilir.
