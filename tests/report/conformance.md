# Uyum Raporu (Conformance Report)

**Oluşturulma Tarihi**: 2026-10-21 20:37:58
**Test Ailesi**: `t-paired`
**%90 Kapısı (yalnızca G*Power kâhinine karşı)**: ❌ KALDI — 33/37 (%89.19)

---

## 1. G*Power Kâhini (`oracle/gpower_vectors.csv`)

| Metrik | Değer |
|---|---|
| Planlı vektör (şablon satırı) | 41 |
| Beklenen değeri dolu vektör | 37 |
| G*Power hata verdi (beklenen alanlar boş) | 4 |
| Tüm alanları eşleşen vektör | 33 |
| Eşleşme oranı (hata vektörleri hariç) | %89.19 |

Karşılaştırılan alanlar: a priori'de N, Df, δ, Critical t, Actual power; post hoc'ta Df, δ, Critical t,
Power. N ve Df tam; diğerleri CSV'deki basamak sayısına kadar.

### 1a. Alan uyuşmazlıkları

| Vektör ID | Mod | Alan | Beklenen (G*Power) | Hesaplanan (motor) | Açıklama |
|---|---|---|---|---|---|
| V21 | a-priori | — | — | HATA | Etki büyüklüğü (dz) kesinlikle pozitif (> 0) olmalıdır, alınan: -0.5 |
| V26 | a-priori | — | — | HATA | Etki büyüklüğü (dz) kesinlikle pozitif (> 0) olmalıdır, alınan: -0.5 |
| V37 | post-hoc | — | — | HATA | Etki büyüklüğü (dz) kesinlikle pozitif (> 0) olmalıdır, alınan: -0.5 |
| V41 | post-hoc | — | — | HATA | Etki büyüklüğü (dz) kesinlikle pozitif (> 0) olmalıdır, alınan: 0.0 |

### 1b. G*Power hata verdi

Bu vektörlerde G*Power girdiyi reddetti; beklenen değer yoktur, orana katılmaz.

| Vektör ID | Mod | Girdi | G*Power mesajı | Motor |
|---|---|---|---|---|
| V17 | a-priori | Two, dz=0.5, α=0.05, Power=0.03 | "Power must be greater than or equal to alpha." (çıktılar ?) | Hata vermeden sonuç döndürüyor: N=2, Df=1, δ=0.7071068, Critical t=12.7062047, power=0.0619486 |
| V25 | a-priori | Two, dz=0, α=0.05, Power=0.80 | "In an a priori analysis, the absolute value of the effect size be greater than 0.00001." (çıktılar ?) | Reddediyor: Etki büyüklüğü (dz) kesinlikle pozitif (> 0) olmalıdır, alınan: 0.0 |
| V29 | post-hoc | Two, dz=0.5, α=0.05, N=2 | "Total sample size is outside the admissible range (3, 2147483646)" (çıktılar ?) | Hata vermeden sonuç döndürüyor: N=2, Df=1, δ=0.7071068, Critical t=12.7062047, power=0.0619486 |
| V40 | post-hoc | Two, dz=0.5, α=0.05, N=1 | "Total sample size is outside the admissible range (3, 2147483646)" (çıktılar ?) | Reddediyor: Örneklem büyüklüğü (n) en az 2 olmalıdır, alınan: 1 |

---

## 2. Self-check (`oracle/selfcheck_scipy.csv`) — KÂHİN DEĞİLDİR

Bu veri, motorla aynı algoritmanın (kesikli N araması + `scipy.stats.nct`) ayrı bir kopyasından
üretilmiştir. Buradaki oran G*Power uyumu hakkında **hiçbir şey söylemez**; yalnızca motorun
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
