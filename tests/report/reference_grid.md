# statsmodels referans ağı (KÂHİN DEĞİL)

Kaynak: `oracle/reference_grid.csv` — KÂHİN DEĞİLDİR: statsmodels TTestPower / FTestPowerF2 ile bağımsız referans ağı (LEDGER L09). Üretici: oracle/generate_reference_grid.py; statsmodels 0.15.0; scipy 1.17.1; numpy 2.4.6; pandas 2.2.3

Kâhin yalnızca G*Power'dır. Bu ağ, yönergedeki "ölçek için 500'den fazla vektör" maddesi içindir: motorun
bağımsız bir kütüphaneyle geniş bir girdi aralığında tutarlı olduğunu gösterir; G*Power uyumunu göstermez
(o: `tests/report/conformance.md`).

| Test | Mod | Vektör | statsmodels geçersiz | Karşılaştırılan | Uyumlu | Uyumsuz |
|---|---|---|---|---|---|---|
| multireg-r2 | a-priori | 48 | 0 | 48 | 48 | 0 |
| multireg-r2 | post-hoc | 120 | 0 | 120 | 120 | 0 |
| t-paired | a-priori | 108 | 0 | 108 | 108 | 0 |
| t-paired | post-hoc | 240 | 17 | 223 | 223 | 0 |
| **Toplam** | | **516** | **17** | **499** | **499** | **0** |

Ölçütler: a priori'de motor N = tavan(statsmodels kesirli N); post hoc'ta |güç farkı| ≤ 1e-6 (gözlenen en büyük fark: 7.22e-16).

## Kesirli N ve yukarı yuvarlama

statsmodels a priori'de N'yi kesirli verir: karşılaştırılan 156 a priori satırından 156 tanesinde
N tamsayı değildir. G*Power ve motor, gücü hedefe ulaştıran en küçük tamsayı N'yi verir; bu, kesirli N'nin
tavanıdır (LEDGER L09). Örnekler (t-paired):

| id | kuyruk | dz | α | hedef güç | statsmodels kesirli N | motor N |
|---|---|---|---|---|---|---|
| G0001 | 1 | 0.1 | 0.01 | 0.8 | 1006.3106 | 1007 |
| G0002 | 1 | 0.1 | 0.01 | 0.9 | 1304.4015 | 1305 |
| G0003 | 1 | 0.1 | 0.01 | 0.95 | 1579.7518 | 1580 |
| G0004 | 1 | 0.1 | 0.05 | 0.8 | 619.6107 | 620 |
| G0005 | 1 | 0.1 | 0.05 | 0.9 | 857.7393 | 858 |
| G0006 | 1 | 0.1 | 0.05 | 0.95 | 1083.5717 | 1084 |

## statsmodels'ın geçersiz satırları

- **Güç 1'e çok yakın, NaN:** çift yönlü `TTestPower.power` büyük dz·√N değerlerinde NaN döndürür.
  Bu satırlar (`sm_valid = 0`) karşılaştırılmaz; motor bu girdilerde 0.9999… ya da 1.0 verir.
- **`FTestPower` serbestlik derecesi takası:** statsmodels'ın eski `FTestPower` sınıfında `df_num` ve
  `df_denom` yer değiştirmiştir (M17 girdisiyle güç 0.0678, kâhin 0.8429603). Ağ `FTestPowerF2` ile
  üretildi; o sınıf M17, M19 ve CONTRACT.md §9 post hoc vektörüyle 7 ondalık aynıdır.
