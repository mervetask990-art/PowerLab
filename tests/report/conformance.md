# Uyum Raporu (Conformance Report)

**Oluşturulma Tarihi**: 2026-10-21 19:55:26
**Test Ailesi**: `t-paired`
**%90 Kapısı (yalnızca G*Power kâhinine karşı)**: ⏳ KISMİ — 9/41 planlı vektör dolu (şu anki oran %100.00); kapı kararı tüm vektörler dolunca verilir

---

## 1. G*Power Kâhini (`oracle/gpower_vectors.csv`)

| Metrik | Değer |
|---|---|
| Planlı vektör (şablon satırı) | 41 |
| Beklenen değeri dolu vektör | 9 |
| Tam N eşleşmesi | 9 |
| Tam N eşleşme oranı | %100.00 |

Uyuşmazlık yok.

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
