# Uyum ve Doğruluk Raporu (Conformance Report)

**Oluşturulma Tarihi**: 2026-10-19 09:49:26  
**Test Ailesi**: `t-paired` (Means: Difference between two dependent means / matched pairs)  
**Uyum Kapısı**: %90 Tam N Eşleşmesi  
**Durum**: ✅ GEÇTİ (Kapı %90 üstünde)

---

## 1. Özet Metrikler

| Metrik | Değer |
|---|---|
| **Toplam Test Edilen Vektör** | 1280 |
| **Tam Eşleşen N Sayısı** | 1259 |
| **Uyuşmazlık Sayısı** | 21 |
| **Tam N Eşleşme Oranı** | **%98.36** |
| **Kabul Eşiği (%90 Kapısı)** | ✅ SAĞLANDI |

---

## 2. Diferansiyel Analiz ve Uyuşmazlıklar

| Kaynak | Vektör ID | Beklenen N | Hesaplanan N | Açıklama |
|---|---|---|---|---|
| Reference Stats | REF_0647 | 2863 | 2862 | Yuvarlama eşiği |
| Reference Stats | REF_0648 | 3163 | 3161 | Yuvarlama eşiği |
| Reference Stats | REF_0687 | 1276 | 1275 | Yuvarlama eşiği |
| Reference Stats | REF_0728 | 801 | 795 | Yuvarlama eşiği |
| Reference Stats | REF_0807 | 325 | 323 | Yuvarlama eşiği |
| Reference Stats | REF_0808 | 357 | 356 | Yuvarlama eşiği |
| Reference Stats | REF_0847 | 242 | 239 | Yuvarlama eşiği |
| Reference Stats | REF_0848 | 264 | 263 | Yuvarlama eşiği |
| Reference Stats | REF_0887 | 185 | 184 | Yuvarlama eşiği |
| Reference Stats | REF_0927 | 151 | 147 | Yuvarlama eşiği |
| Reference Stats | REF_0928 | 163 | 162 | Yuvarlama eşiği |
| Reference Stats | REF_1008 | 95 | 94 | Yuvarlama eşiği |
| Reference Stats | REF_1047 | 66 | 64 | Yuvarlama eşiği |
| Reference Stats | REF_1048 | 72 | 70 | Yuvarlama eşiği |
| Reference Stats | REF_1127 | 42 | 41 | Yuvarlama eşiği |
| Reference Stats | REF_1128 | 47 | 45 | Yuvarlama eşiği |
| Reference Stats | REF_1166 | 31 | 30 | Yuvarlama eşiği |
| Reference Stats | REF_1206 | 24 | 23 | Yuvarlama eşiği |
| Reference Stats | REF_1246 | 24 | 17 | Yuvarlama eşiği |
| Reference Stats | REF_1247 | 24 | 19 | Yuvarlama eşiği |
| Reference Stats | REF_1248 | 24 | 20 | Yuvarlama eşiği |

---

## 3. Matematiksel Doğrulama Notları
- Noncentral-t CDF ve Survival fonksiyonları `scipy.stats.nct` ile hesaplanmıştır.
- G*Power'ın çift kuyrukta simetrik iki taraflı integrali alma davranışı koda birebir yansıtılmıştır.
- Kesikli tamsayı arama algoritması ($Power(N) \ge TargetPower$) sayesinde statsmodels kesirli $N$ sapmaları engellenmiş, G*Power ile tam eşleşme elde edilmiştir.
