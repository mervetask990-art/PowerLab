# G*Power Vektör Toplama Listesi (t-paired)

**Test seçimi:** Test family = `t tests` → Statistical test = `Means: Difference between two dependent means (matched pairs)`

**Kayıt:** Her vektörde G*Power penceresinin tamamını (Input + Output Parameters görünür) `Vxx.png` adıyla şu klasöre kaydedin: `C:\Users\User\Desktop\rea_test\oracle\screenshots\`

**Sıra:** Önce tüm A priori'ler (Bölüm 1), sonra tüm Post hoc'lar (Bölüm 2); mod yalnızca bir kez değişir. Değerleri ondalık **nokta** ile girin (V01'de böyle).

**Hata/uyarı veren girdiler (⚠):** G*Power uyarı kutusu açarsa ya da hesaplamayı reddederse, ekran görüntüsünde o kutu ve girdiler birlikte görünsün. Output alanları boş kalsa da kaydedin.

## 1. A priori — `A priori: Compute required sample size – given α, power, and effect size`

| ✓ | ID | Type of power analysis | Tail(s) | Effect size dz | α err prob | Power (1-β err prob) | Not |
|---|---|---|---|---|---|---|---|
| [x] | V01 | A priori | Two | 0.5 | 0.05 | 0.95 | Standart orta etki çift kuyruk — G*Power 3.1.9.7 Output Parameters paneli, 7 ondalık |
| [x] | V02 | A priori | One | 0.5 | 0.05 | 0.95 | Tek kuyruk eşi: V01 |
| [x] | V03 | A priori | Two | 0.5 | 0.05 | 0.80 | Standart 0.80 güç; tek kuyruk eşi V04 |
| [x] | V04 | A priori | One | 0.5 | 0.05 | 0.80 | Tek kuyruk eşi: V03 |
| [x] | V05 | A priori | Two | 0.2 | 0.05 | 0.80 | Küçük etki; tek kuyruk eşi V06 |
| [x] | V06 | A priori | One | 0.2 | 0.05 | 0.80 | Tek kuyruk eşi: V05 |
| [x] | V07 | A priori | Two | 0.01 | 0.05 | 0.80 | dz çok küçük (N on binlerce); boundary B01 ile aynı girdi |
| [x] | V08 | A priori | Two | 0.05 | 0.05 | 0.80 | dz çok küçük |
| [x] | V09 | A priori | Two | 0.1 | 0.05 | 0.80 | dz çok küçük |
| [x] | V10 | A priori | Two | 1.5 | 0.05 | 0.80 | dz çok büyük |
| [x] | V11 | A priori | Two | 2 | 0.05 | 0.80 | dz çok büyük |
| [x] | V12 | A priori | Two | 3 | 0.05 | 0.80 | dz çok büyük |
| [x] | V13 | A priori | Two | 5 | 0.05 | 0.99 | dz çok büyük (N minimuma iner); boundary B02 ile aynı girdi |
| [x] | V14 | A priori | Two | 0.5 | 0.05 | 0.99 | Güç çok yüksek |
| [x] | V15 | A priori | Two | 0.5 | 0.05 | 0.999 | Güç çok yüksek |
| [x] | V16 | A priori | Two | 0.5 | 0.05 | 0.05 | Güç = α; boundary B04 ile aynı girdi |
| [x] | V17 | A priori | Two | 0.5 | 0.05 | 0.03 | Güç < α — G*Power Input error: "Power must be greater than or equal to alpha." (çıktılar ?) |
| [x] | V18 | A priori | Two | 0.5 | 0.001 | 0.80 | α alt ucu |
| [x] | V19 | A priori | Two | 0.5 | 0.2 | 0.80 | α üst ucu; tek kuyruk eşi V20 |
| [x] | V20 | A priori | One | 0.5 | 0.2 | 0.80 | Tek kuyruk eşi: V19 |
| [x] | V21 | A priori | One | -0.5 | 0.05 | 0.80 | ⚠ Tek kuyrukta negatif dz (G*Power tepkisi kaydedilecek) |
| [x] | V22 | A priori | One | 0.25 | 0.01 | 0.90 | Sınır vakası: güç hedefi çok ince farkla aşıyor (girdi motorla seçildi; beklenen değer G*Power'dan) |
| [x] | V23 | A priori | One | 0.3 | 0.1 | 0.95 | Sınır vakası: güç hedefi çok ince farkla aşıyor (girdi motorla seçildi; beklenen değer G*Power'dan) |
| [x] | V24 | A priori | Two | 0.5 | 0.05 | 0.90 | Sınır vakası: güç hedefi çok ince farkla aşıyor (girdi motorla seçildi; beklenen değer G*Power'dan) |
| [x] | V25 | A priori | Two | 0 | 0.05 | 0.80 | ⚠ GEÇERSİZ GİRDİ (boundary B07): dz=0; ekran görüntüsü G*Power'ın tepkisini göstermeli — G*Power Input error: "In an a priori analysis, the absolute value of the effect size be greater than 0.00001." (çıktılar ?) |
| [x] | V26 | A priori | Two | -0.5 | 0.05 | 0.80 | ⚠ GEÇERSİZ GİRDİ (boundary B06): çift kuyrukta negatif dz; ekran görüntüsü G*Power'ın tepkisini göstermeli |

## 2. Post hoc — `Post hoc: Compute achieved power – given α, sample size, and effect size`

| ✓ | ID | Type of power analysis | Tail(s) | Effect size dz | α err prob | Total sample size | Not |
|---|---|---|---|---|---|---|---|
| [ ] | V27 | Post hoc | Two | 0.5 | 0.05 | 30 | Post hoc standart; tek kuyruk eşi V28 |
| [ ] | V28 | Post hoc | One | 0.5 | 0.05 | 30 | Tek kuyruk eşi: V27 |
| [ ] | V29 | Post hoc | Two | 0.5 | 0.05 | 2 | Post hoc N=2 (df=1) |
| [ ] | V30 | Post hoc | Two | 0.5 | 0.05 | 3 | Post hoc N=3 |
| [ ] | V31 | Post hoc | Two | 0.1 | 0.05 | 1000 | Post hoc N=1000; tek kuyruk eşi V32 |
| [ ] | V32 | Post hoc | One | 0.1 | 0.05 | 1000 | Tek kuyruk eşi: V31 |
| [ ] | V33 | Post hoc | Two | 0.01 | 0.05 | 100 | dz çok küçük (güç ≈ α) |
| [ ] | V34 | Post hoc | Two | 3 | 0.05 | 5 | dz çok büyük, küçük N |
| [ ] | V35 | Post hoc | Two | 0.5 | 0.001 | 50 | α alt ucu |
| [ ] | V36 | Post hoc | Two | 0.5 | 0.2 | 20 | α üst ucu |
| [ ] | V37 | Post hoc | One | -0.5 | 0.05 | 30 | ⚠ Tek kuyrukta negatif dz (G*Power tepkisi kaydedilecek) |
| [ ] | V38 | Post hoc | Two | 0.2 | 0.05 | 100 | Orta N; tek kuyruk eşi V39 |
| [ ] | V39 | Post hoc | One | 0.2 | 0.05 | 100 | Tek kuyruk eşi: V38 |
| [ ] | V40 | Post hoc | Two | 0.5 | 0.05 | 1 | ⚠ GEÇERSİZ GİRDİ (boundary B13): N=1 (df=0); ekran görüntüsü G*Power'ın tepkisini göstermeli |
| [ ] | V41 | Post hoc | Two | 0 | 0.05 | 30 | ⚠ dz=0 post hoc (G*Power gücü α olarak verebilir ya da hata verebilir; tepki kaydedilecek) |

---

Toplam 41 vektör: 26 A priori, 15 Post hoc. Bu liste `oracle/gpower_vectors.csv`'den üretilmiştir; girdiler CSV ile birebir aynıdır. Okuma ve onay adımları için bkz. `CLAUDE.md` → "Kâhin vektörü işleme".
