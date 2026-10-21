# Uyum Raporu (Conformance Report)

**Oluşturulma Tarihi**: 2026-10-21 21:47:28
**Test Ailesi**: `t-paired`
**%90 Kapısı (yalnızca G*Power kâhinine karşı)**: ✅ GEÇTİ — 33/34 (%97.06)

---

## 1. G*Power Kâhini (`oracle/gpower_vectors.csv`)

| Metrik | Değer |
|---|---|
| Planlı vektör (şablon satırı) | 43 |
| Beklenen değeri dolu, karşılaştırılan vektör | 34 |
| Sözleşme gereği kasıtlı sapma (orana katılmaz) | 5 |
| G*Power hata verdi (beklenen alanlar boş) | 4 |
| Tüm alanları eşleşen vektör | 33 |
| Eşleşme oranı (hata vektörleri ve kasıtlı sapmalar hariç) | %97.06 |

Karşılaştırılan alanlar: a priori'de N, Df, δ, Critical t, Actual power; post hoc'ta Df, δ, Critical t,
Power. N ve Df tam; diğerleri CSV'deki basamak sayısına kadar.

### 1a. Alan uyuşmazlıkları

| Vektör ID | Mod | Alan | Beklenen (G*Power) | Hesaplanan (motor) | Açıklama |
|---|---|---|---|---|---|
| V42 | a-priori | N | 78488272181 | 78488605096 | Bilinen uyuşmazlık: çok büyük df'de (≈ 7.8·10¹⁰) G*Power bu N'de gücü 0.8000265 gösteriyor, scipy aynı N'de hedefin altında hesaplıyor; motor hedefi daha büyük N'de buluyor (LEDGER L17, açık soru Q7). Düzeltilmedi. |
| V42 | a-priori | Df | 78488272180 | 78488605095 | Bilinen uyuşmazlık: çok büyük df'de (≈ 7.8·10¹⁰) G*Power bu N'de gücü 0.8000265 gösteriyor, scipy aynı N'de hedefin altında hesaplıyor; motor hedefi daha büyük N'de buluyor (LEDGER L17, açık soru Q7). Düzeltilmedi. |
| V42 | a-priori | δ | 2.8015758 | 2.8015817870624447 | Bilinen uyuşmazlık: çok büyük df'de (≈ 7.8·10¹⁰) G*Power bu N'de gücü 0.8000265 gösteriyor, scipy aynı N'de hedefin altında hesaplıyor; motor hedefi daha büyük N'de buluyor (LEDGER L17, açık soru Q7). Düzeltilmedi. |
| V42 | a-priori | Actual power | 0.8000265 | 0.8000000000040838 | Bilinen uyuşmazlık: çok büyük df'de (≈ 7.8·10¹⁰) G*Power bu N'de gücü 0.8000265 gösteriyor, scipy aynı N'de hedefin altında hesaplıyor; motor hedefi daha büyük N'de buluyor (LEDGER L17, açık soru Q7). Düzeltilmedi. |

### 1b. G*Power hata verdi

Bu vektörlerde G*Power girdiyi reddetti; beklenen değer yoktur, orana katılmaz.

| Vektör ID | Mod | Girdi | G*Power mesajı | Motor |
|---|---|---|---|---|
| V17 | a-priori | Two, dz=0.5, α=0.05, Power=0.03 | "Power must be greater than or equal to alpha." (çıktılar ?) | Reddediyor (INCONSISTENT): Power (güç) alpha değerinden küçük olamaz (power >= alpha olmalıdır), alınan: power=0.03, alpha=0.05 |
| V25 | a-priori | Two, dz=0, α=0.05, Power=0.80 | "In an a priori analysis, the absolute value of the effect size be greater than 0.00001." (çıktılar ?) | Reddediyor (OUT_OF_RANGE): Etki büyüklüğü (dz) pozitif olmalıdır (dz > 0), alınan: 0.0 |
| V29 | post-hoc | Two, dz=0.5, α=0.05, N=2 | "Total sample size is outside the admissible range (3, 2147483646)" (çıktılar ?) | Reddediyor (OUT_OF_RANGE): Örneklem büyüklüğü (n) izin verilen aralığın dışında: en az 3 olmalıdır, alınan: 2 |
| V40 | post-hoc | Two, dz=0.5, α=0.05, N=1 | "Total sample size is outside the admissible range (3, 2147483646)" (çıktılar ?) | Reddediyor (OUT_OF_RANGE): Örneklem büyüklüğü (n) izin verilen aralığın dışında: en az 3 olmalıdır, alınan: 1 |

### 1c. Sözleşme gereği kasıtlı sapma

CONTRACT.md §5 `dz > 0` ister. G*Power negatif dz'yi ve post hoc'ta dz = 0'ı kabul edip hesap yapar
(LEDGER L13, L16); motor sözleşme gereği `OUT_OF_RANGE` döner. Eğitmene soruldu. Kâhin değerleri değişmedi;
bu vektörler %90 kapısına katılmaz.

| Vektör ID | Mod | Girdi | G*Power (kâhin, değişmedi) | Motor |
|---|---|---|---|---|
| V21 | a-priori | One, dz=-0.5, α=0.05, Power=0.80 | N=27, Df=26, δ=-2.5980762, Critical t=-1.7056179, power=0.8118316 | Reddediyor (OUT_OF_RANGE): Etki büyüklüğü (dz) pozitif olmalıdır (dz > 0), alınan: -0.5 |
| V26 | a-priori | Two, dz=-0.5, α=0.05, Power=0.80 | N=34, Df=33, δ=-2.9154759, Critical t=-2.0345153, power=0.8077775 | Reddediyor (OUT_OF_RANGE): Etki büyüklüğü (dz) pozitif olmalıdır (dz > 0), alınan: -0.5 |
| V37 | post-hoc | One, dz=-0.5, α=0.05, N=30 | Df=29, δ=-2.7386128, Critical t=-1.6991270, power=0.8482542 | Reddediyor (OUT_OF_RANGE): Etki büyüklüğü (dz) pozitif olmalıdır (dz > 0), alınan: -0.5 |
| V41 | post-hoc | Two, dz=0, α=0.05, N=30 | Df=29, δ=0, Critical t=2.0452296, power=0.0500000 | Reddediyor (OUT_OF_RANGE): Etki büyüklüğü (dz) pozitif olmalıdır (dz > 0), alınan: 0.0 |
| V43 | post-hoc | One, dz=0, α=0.05, N=30 | Df=29, δ=0, Critical t=1.6991270, power=0.0500000 | Reddediyor (OUT_OF_RANGE): Etki büyüklüğü (dz) pozitif olmalıdır (dz > 0), alınan: 0.0 |

---

## 2. Eğitmen Protokolü (`oracle/public_vectors.jsonl`, CONTRACT.md §9)

Karşılaştırma CONTRACT.md §6: tam sayılar tam eşleşme; ondalıklar |fark| ≤ 1e-6 ya da göreli ≤ 1e-6.
Uygulanan: t-paired a-priori ve post-hoc; diğer aile ve modlar `UNSUPPORTED` döner.
**Uyumlu: 2/2 uygulanan vektör** (25 vektörün 23'i `UNSUPPORTED`).

| Vektör ID | Durum | Ayrıntı |
|---|---|---|
| t2-indep/a-priori | UNSUPPORTED | t2-indep bu motorda henüz uygulanmadı |
| t2-indep/post-hoc | UNSUPPORTED | t2-indep bu motorda henüz uygulanmadı |
| t2-indep/compromise | UNSUPPORTED | t2-indep bu motorda henüz uygulanmadı |
| t2-indep/criterion | UNSUPPORTED | t2-indep bu motorda henüz uygulanmadı |
| t2-indep/sensitivity | UNSUPPORTED | t2-indep bu motorda henüz uygulanmadı |
| t-paired/a-priori | UYUMLU | tüm alanlar §6 toleransında |
| t-paired/post-hoc | UYUMLU | tüm alanlar §6 toleransında |
| t-paired/compromise | UNSUPPORTED | t-paired için compromise modu bu motorda henüz uygulanmadı |
| t-paired/criterion | UNSUPPORTED | t-paired için criterion modu bu motorda henüz uygulanmadı |
| t-paired/sensitivity | UNSUPPORTED | t-paired için sensitivity modu bu motorda henüz uygulanmadı |
| anova-oneway/a-priori | UNSUPPORTED | anova-oneway bu motorda henüz uygulanmadı |
| anova-oneway/post-hoc | UNSUPPORTED | anova-oneway bu motorda henüz uygulanmadı |
| anova-oneway/compromise | UNSUPPORTED | anova-oneway bu motorda henüz uygulanmadı |
| anova-oneway/criterion | UNSUPPORTED | anova-oneway bu motorda henüz uygulanmadı |
| anova-oneway/sensitivity | UNSUPPORTED | anova-oneway bu motorda henüz uygulanmadı |
| chi2-contingency/a-priori | UNSUPPORTED | chi2-contingency bu motorda henüz uygulanmadı |
| chi2-contingency/post-hoc | UNSUPPORTED | chi2-contingency bu motorda henüz uygulanmadı |
| chi2-contingency/compromise | UNSUPPORTED | chi2-contingency bu motorda henüz uygulanmadı |
| chi2-contingency/criterion | UNSUPPORTED | chi2-contingency bu motorda henüz uygulanmadı |
| chi2-contingency/sensitivity | UNSUPPORTED | chi2-contingency bu motorda henüz uygulanmadı |
| multireg-r2/a-priori | UNSUPPORTED | multireg-r2 bu motorda henüz uygulanmadı |
| multireg-r2/post-hoc | UNSUPPORTED | multireg-r2 bu motorda henüz uygulanmadı |
| multireg-r2/compromise | UNSUPPORTED | multireg-r2 bu motorda henüz uygulanmadı |
| multireg-r2/criterion | UNSUPPORTED | multireg-r2 bu motorda henüz uygulanmadı |
| multireg-r2/sensitivity | UNSUPPORTED | multireg-r2 bu motorda henüz uygulanmadı |

---

## 3. Self-check (`oracle/selfcheck_scipy.csv`) — KÂHİN DEĞİLDİR

Bu veri, motorla aynı algoritmanın (kesikli N araması + `scipy.stats.nct`) ayrı bir kopyasından
üretilmiştir (motor `scipy.special` kullanır; `scipy.stats` aynı özel fonksiyonları çağırır). Buradaki oran G*Power uyumu hakkında **hiçbir şey söylemez**; yalnızca motorun
bağımsız bir yeniden yazımla tutarlılığını gösterir.

| Metrik | Değer |
|---|---|
| Toplam vektör | 1280 |
| Tam N eşleşmesi | 1259 |
| Tam N eşleşme oranı | %98.36 |

| Vektör ID | Beklenen N | Hesaplanan N | Açıklama |
|---|---|---|---|
| REF_0647 | 2863 | 2862 | Üretici betikte sol kuyruk NaN koruması yok: nct.cdf(-t_crit) NaN dönünce güç NaN olur, `NaN >= hedef` False verir ve betik N'yi gereğinden büyük seçer. Motor NaN'ı 0.0 kabul eder. |
| REF_0648 | 3163 | 3161 | Üretici betikte sol kuyruk NaN koruması yok: nct.cdf(-t_crit) NaN dönünce güç NaN olur, `NaN >= hedef` False verir ve betik N'yi gereğinden büyük seçer. Motor NaN'ı 0.0 kabul eder. |
| REF_0687 | 1276 | 1275 | Üretici betikte sol kuyruk NaN koruması yok: nct.cdf(-t_crit) NaN dönünce güç NaN olur, `NaN >= hedef` False verir ve betik N'yi gereğinden büyük seçer. Motor NaN'ı 0.0 kabul eder. |
| REF_0728 | 801 | 795 | Üretici betikte sol kuyruk NaN koruması yok: nct.cdf(-t_crit) NaN dönünce güç NaN olur, `NaN >= hedef` False verir ve betik N'yi gereğinden büyük seçer. Motor NaN'ı 0.0 kabul eder. |
| REF_0807 | 325 | 323 | Üretici betikte sol kuyruk NaN koruması yok: nct.cdf(-t_crit) NaN dönünce güç NaN olur, `NaN >= hedef` False verir ve betik N'yi gereğinden büyük seçer. Motor NaN'ı 0.0 kabul eder. |
| REF_0808 | 357 | 356 | Üretici betikte sol kuyruk NaN koruması yok: nct.cdf(-t_crit) NaN dönünce güç NaN olur, `NaN >= hedef` False verir ve betik N'yi gereğinden büyük seçer. Motor NaN'ı 0.0 kabul eder. |
| REF_0847 | 242 | 239 | Üretici betikte sol kuyruk NaN koruması yok: nct.cdf(-t_crit) NaN dönünce güç NaN olur, `NaN >= hedef` False verir ve betik N'yi gereğinden büyük seçer. Motor NaN'ı 0.0 kabul eder. |
| REF_0848 | 264 | 263 | Üretici betikte sol kuyruk NaN koruması yok: nct.cdf(-t_crit) NaN dönünce güç NaN olur, `NaN >= hedef` False verir ve betik N'yi gereğinden büyük seçer. Motor NaN'ı 0.0 kabul eder. |
| REF_0887 | 185 | 184 | Üretici betikte sol kuyruk NaN koruması yok: nct.cdf(-t_crit) NaN dönünce güç NaN olur, `NaN >= hedef` False verir ve betik N'yi gereğinden büyük seçer. Motor NaN'ı 0.0 kabul eder. |
| REF_0927 | 151 | 147 | Üretici betikte sol kuyruk NaN koruması yok: nct.cdf(-t_crit) NaN dönünce güç NaN olur, `NaN >= hedef` False verir ve betik N'yi gereğinden büyük seçer. Motor NaN'ı 0.0 kabul eder. |
| REF_0928 | 163 | 162 | Üretici betikte sol kuyruk NaN koruması yok: nct.cdf(-t_crit) NaN dönünce güç NaN olur, `NaN >= hedef` False verir ve betik N'yi gereğinden büyük seçer. Motor NaN'ı 0.0 kabul eder. |
| REF_1008 | 95 | 94 | Üretici betikte sol kuyruk NaN koruması yok: nct.cdf(-t_crit) NaN dönünce güç NaN olur, `NaN >= hedef` False verir ve betik N'yi gereğinden büyük seçer. Motor NaN'ı 0.0 kabul eder. |
| REF_1047 | 66 | 64 | Üretici betikte sol kuyruk NaN koruması yok: nct.cdf(-t_crit) NaN dönünce güç NaN olur, `NaN >= hedef` False verir ve betik N'yi gereğinden büyük seçer. Motor NaN'ı 0.0 kabul eder. |
| REF_1048 | 72 | 70 | Üretici betikte sol kuyruk NaN koruması yok: nct.cdf(-t_crit) NaN dönünce güç NaN olur, `NaN >= hedef` False verir ve betik N'yi gereğinden büyük seçer. Motor NaN'ı 0.0 kabul eder. |
| REF_1127 | 42 | 41 | Üretici betikte sol kuyruk NaN koruması yok: nct.cdf(-t_crit) NaN dönünce güç NaN olur, `NaN >= hedef` False verir ve betik N'yi gereğinden büyük seçer. Motor NaN'ı 0.0 kabul eder. |
| REF_1128 | 47 | 45 | Üretici betikte sol kuyruk NaN koruması yok: nct.cdf(-t_crit) NaN dönünce güç NaN olur, `NaN >= hedef` False verir ve betik N'yi gereğinden büyük seçer. Motor NaN'ı 0.0 kabul eder. |
| REF_1166 | 31 | 30 | Üretici betikte sol kuyruk NaN koruması yok: nct.cdf(-t_crit) NaN dönünce güç NaN olur, `NaN >= hedef` False verir ve betik N'yi gereğinden büyük seçer. Motor NaN'ı 0.0 kabul eder. |
| REF_1206 | 24 | 23 | Üretici betikte sol kuyruk NaN koruması yok: nct.cdf(-t_crit) NaN dönünce güç NaN olur, `NaN >= hedef` False verir ve betik N'yi gereğinden büyük seçer. Motor NaN'ı 0.0 kabul eder. |
| REF_1246 | 24 | 17 | Üretici betikte sol kuyruk NaN koruması yok: nct.cdf(-t_crit) NaN dönünce güç NaN olur, `NaN >= hedef` False verir ve betik N'yi gereğinden büyük seçer. Motor NaN'ı 0.0 kabul eder. |
| REF_1247 | 24 | 19 | Üretici betikte sol kuyruk NaN koruması yok: nct.cdf(-t_crit) NaN dönünce güç NaN olur, `NaN >= hedef` False verir ve betik N'yi gereğinden büyük seçer. Motor NaN'ı 0.0 kabul eder. |
| REF_1248 | 24 | 20 | Üretici betikte sol kuyruk NaN koruması yok: nct.cdf(-t_crit) NaN dönünce güç NaN olur, `NaN >= hedef` False verir ve betik N'yi gereğinden büyük seçer. Motor NaN'ı 0.0 kabul eder. |
