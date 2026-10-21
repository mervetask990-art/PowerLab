# CONTRACT_ASSUMED: Varsayılan CLI Sözleşmesi

> ⚠️ **Resmi CONTRACT.md gelince bu dosya güncellenecek.** Buradaki her kural, resmi sözleşme
> gelene kadar geçerli olan bir **varsayımdır**. Resmi metinle çelişen her madde resmi metne göre
> değiştirilir.

## 0. Tek dış kaynak

Ödev metnindeki tek örnek (t2-indep; bu projede t2-indep uygulanmıyor):

```
gpower-clone --test t2-indep --mode a-priori --tails 2 --d 0.5 --alpha 0.05 --power 0.95 --ratio 1
→ {"n1":105,"n2":105,"n_total":210,"actual_power":0.9501,"critical":1.9714,"df":208,"ncp":3.6228}
```

Kaynak ödev metnidir; G*Power ekran görüntüsü değildir. Aşağıdaki kurallar bu örnekteki kalıptan
çıkarılmıştır.

---

## 1. Çağrı kalıbı

| # | Varsayım | Gerekçe |
|---|---|---|
| C1 | Komut adı `gpower-clone`. | Örnek bu adla çağırıyor; hocanın otomatik düzeneği de bu adı kullanıyor (bkz. `prompts/NOTLAR.md`). |
| C2 | Biçim: `--test <aile> --mode <mod> [--tails] <etki> --alpha <α> (--power <1-β> \| --n <N>) [aileye özel]`. | Örnekteki parametre sırası ve adları. Post-hoc için örnek yok; `--n`, a-priori'deki `--power`'ın yerini alır. |
| C3 | `--mode` şu değerlerden birini alır: `a-priori`, `a_priori`, `apriori`, `post-hoc`, `post_hoc`, `posthoc`. | Örnek `a-priori` kullanıyor; düzenek başka bir yazım da gönderebilir. |

## 2. Parametre adları ve takma adlar

| Aile | Anlam | Kabul edilen adlar | Gerekçe |
|---|---|---|---|
| t-paired | Etki büyüklüğü dz | `--dz`, `--d`, `--effect` | Örnek t testinde `--d` kullanıyor; G*Power t-paired'de bu değeri "dz" diye adlandırıyor. |
| multireg-r2 | Etki büyüklüğü f² | `--f2`, `--effect` | G*Power "Effect size f²" diyor. |
| multireg-r2 | Yordayıcı sayısı | `--predictors`, `--u`, `--k` | G*Power "Number of predictors" diyor; literatürde u (pay df) ya da k olarak geçiyor. |
| Tümü | Post-hoc örneklem büyüklüğü | `--n`, `--n-total` | Çıktıdaki `n_total` alanıyla simetrik olsun diye. |

- **C4**: Aynı anlamdaki iki ad **farklı değerle** verilirse hata döner (çıkış kodu 2). Aynı değerle
  verilirse sorun yoktur. Gerekçe: hangi değerin kastedildiği belirsizdir; sessizce birini seçmek
  hatayı gizler.
- **C5**: `--effect` aileye göre çözülür: t-paired'de dz, multireg-r2'de f² anlamına gelir.

## 3. Aileye ait olmayan parametreler (tolerans kuralları)

**İlke:** Gizli düzenek tüm çağrılara ortak parametreler ekleyebilir. Bu nedenle **zararsız**
olanlar yok sayılır, **anlamsız** olanlar hata verir. Yok sayılan parametreler çıktıya hiçbir şey
eklemez; stdout yine tek satır JSON'dur, stderr boştur.

| # | Aile | Parametre | Davranış | Gerekçe |
|---|---|---|---|---|
| T1 | t-paired | `--ratio 1` | Yok sayılır | Örnekte ortak parametre olarak geçiyor; eşleştirilmiş tasarımda tek grup vardır, oran 1 zararsızdır. |
| T2 | t-paired | `--ratio` ≠ 1 | Hata (2) | Eşleştirilmiş tasarımda grup oranı tanımsızdır; 1'den farklı bir değer, yanlış testin seçildiğini gösterir. |
| T3 | t-paired | `--f2`, `--predictors`, `--u`, `--k` | Hata (2) | Regresyona özgü parametrelerdir; verilmeleri test ailesinin karıştırıldığını gösterir. |
| T4 | multireg-r2 | `--tails 1` veya `--tails 2` | Yok sayılır | F testi zaten tek yönlüdür; G*Power bu test için kuyruk sormaz. Ortak parametre olarak gelebilir. |
| T5 | multireg-r2 | `--tails` ∉ {1, 2} | Hata (2) | Hiçbir testte geçerli bir değer değildir. |
| T6 | multireg-r2 | `--ratio 1` | Yok sayılır | T1 ile aynı gerekçe. |
| T7 | multireg-r2 | `--ratio` ≠ 1 | Hata (2) | Tek örneklemli regresyonda grup oranı tanımsızdır. |
| T8 | multireg-r2 | `--dz`, `--d` | Hata (2) | t testine özgü etki büyüklükleridir; f² ile karıştırılması ciddi bir hatadır. |

## 4. JSON çıktısı

| # | Varsayım | Gerekçe |
|---|---|---|
| J1 | Çıktı stdout'a yazılan tek satır JSON'dur; alan sırası sabittir ve fazladan alan yoktur. | Örnek tek satır ve sıralı. |
| J2 | `n_total` her ailede vardır. | Örnekte var; toplam örneklemi aileden bağımsız ifade eder. |
| J3 | **t-paired**: `n, n_total, actual_power, critical, df, ncp` (n = n_total = çift sayısı). | Tek grup olduğu için n1/n2 anlamsızdır. `n` ailelerin tutarlı olması için kalır. |
| J4 | **multireg-r2**: `n, n_total, actual_power, critical, df1, df2, ncp` (n = n_total). | F testinin iki serbestlik derecesi vardır (pay df1 = u, payda df2 = N − u − 1). Örnekteki tek `df` alanı t testlerine özgüdür. `n`, t-paired ile tutarlılık için var. **Motor henüz yok**; şimdilik `{"error":"multireg-r2 henüz uygulanmadı"}` döner. |
| J5 | JSON ASCII kaçışlıdır (`ensure_ascii=True`); Türkçe karakterler `\u00fc` biçiminde görünür. | Windows konsolunda kod sayfasından bağımsız çalışır. |

## 5. Ondalık basamak

| # | Varsayım | Gerekçe |
|---|---|---|
| D1 | `actual_power`, `critical` ve `ncp` **7 basamağa** yuvarlanır. Bu değer tek bir sabitten yönetilir: `OUTPUT_DECIMALS` (`src/powerlab/engine/rounding.py`). | **Kanıt: `oracle/screenshots/V01.png`.** G*Power 3.1.9.7'nin Output Parameters paneli bu üç alanı 7 ondalıkla gösteriyor (δ = 3.6742346, Critical t = 2.0057460, Actual power = 0.9502120). Hoca toleransı "G*Power'ın ekranda gösterdiği basamak sayısına kadar" olarak tanımladığı için karşılaştırma 7 basamakta sayısal yapılır. Önceki 6 basamak ncp'de yetersiz kaldı (3.674235 ≠ 3.6742346). Ödev metnindeki örneğin 4 basamağı, ekran kanıtı karşısında bağlayıcı değildir. |
| D2 | Her yeni kâhin vektöründe basamak sayısı ekran görüntüsünden okunup `oracle/gpower_vectors.csv`'ye **metin olarak aynen** yazılır (sondaki sıfırlar dahil, ör. `2.0057460`). Diferansiyel test o basamak sayısına kadar karşılaştırır. | Başka bir test ailesi ya da alan farklı sayıda basamak gösterirse D1 o kanıta göre güncellenir. Şu an tek kanıt V01'dir (t-paired, a-priori). |
| D3 | JSON sayısal değer taşır, metin değil: `2.0057460`, JSON'da `2.005746` olarak görünür (sondaki sıfır düşer). Değer aynıdır. | Hocanın karşılaştırması sayısal (D1). Biçimi metin olarak birebir taklit etmek gerekirse resmi CONTRACT.md'ye göre yeniden değerlendirilir. |
| D4 | Grafik başlığındaki `critical t = 2.00575` (5 basamak) **kâhin olarak kullanılmaz**; yalnızca Output Parameters paneli esas alınır. | Aynı ekranda iki farklı biçim var. Sayısal sonucu bildiren alan paneldir; başlık bir grafik etiketidir. |

## 6. Hatalar ve çıkış kodları

| # | Varsayım | Gerekçe |
|---|---|---|
| E1 | Hata durumunda stdout'a `{"error":"..."}` yazılır; stderr'e hiçbir şey yazılmaz. | Çift çıktı olmaz; düzenek tek bir akışı okur. |
| E2 | Çıkış kodu `1`: hesap ya da doğrulama hatası (a priori'de \|dz\| < 0.00001, a priori'de hedef güç < α, post hoc'ta N < 3, NaN/inf, eksik etki büyüklüğü, desteklenmeyen ya da henüz uygulanmamış aile). Negatif dz ve post hoc'ta dz = 0 hata **değildir**. | G*Power tepkileri: V17, V25, V29, V40 hata; V21, V26, V37, V41, V42, V43 kabul (LEDGER L12–L16). |
| E3 | Çıkış kodu `2`: argüman hatası (bilinmeyen parametre, eksik zorunlu parametre, geçersiz seçenek ya da tür, çakışan takma adlar, aileye ait olmayan anlamsız parametre). | argparse geleneği. |
| E4 | `--help` normal metin yazar ve `0` ile çıkar. | |
| E5 | Negatif ya da sonsuz değerler `=` biçimiyle verilir (`--dz=-0.5`, `--dz=-inf`). Negatif dz geçerli bir girdidir (E2). | argparse, ayrı yazılmış `-inf`'i bayrak sanır. |
