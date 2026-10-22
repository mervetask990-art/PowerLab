# oracle/

| Dosya | Statü | Açıklama |
|---|---|---|
| `gpower_vectors.csv` + `screenshots/` | **KÂHİN** | G*Power 3.1.9.7 ekran görüntüleri (CLAUDE.md "Kâhin") |
| `public_vectors.jsonl` | **KÂHİN** | Eğitmen protokolü, CONTRACT.md §9'dan birebir; bkz. `public_vectors.README.md` |
| `reference_statsmodels.csv` | **KÂHİN DEĞİL** | statsmodels ile bağımsız çapraz kontrol (aşağıda) |
| `selfcheck_scipy.csv` | **KÂHİN DEĞİL** | Motorla aynı algoritmanın kopyası; yalnızca kendi kendine tutarlılık |
| `boundary_vectors.csv` | — | Sınır değer senaryoları |
| `_dogrulanmamis/legacy_vectors.csv` | **KÂHİN DEĞİL** | Ekran görüntüsü olmayan eski değerler; hiçbir testte kullanılmaz |

## reference_statsmodels.csv: KÂHİN DEĞİLDİR

- **Ne:** t-paired için `statsmodels.stats.power.TTestPower` çıktıları. Motorun bağımsız bir kütüphaneyle
  **çapraz kontrolüdür**; G*Power uyumu hakkında bir şey kanıtlamaz. Kâhin yalnızca G*Power'dır.
- **Girdiler:** `gpower_vectors.csv` içinde G*Power'ın değer ürettiği ve CONTRACT.md §5'e uygun (dz > 0)
  34 t-paired vektörü (23 a priori, 11 post hoc). Dışarıda: dz ≤ 0 olan kasıtlı sapmalar (V21, V26, V37,
  V41, V43) ve G*Power'ın hata verdiği vektörler (V17, V25, V29, V40).
- **Sütunlar:** a priori'de `sm_n_fractional` (statsmodels `solve_power`, kesirli N), `sm_n_ceil` (tavanı),
  `sm_power` (tavan N'de güç); post hoc'ta `sm_power`. `sm_warnings`: statsmodels uyarı/hata metni, aynen.
- **Bilinen fark (LEDGER L09):** statsmodels a priori'de kesirli N verir; G*Power tamsayı N verir (tavan) ve
  gücü bu N ile günceller. Bu yüzden test a priori'de **tavan(kesirli N) = motor N**, post hoc'ta
  **|güç farkı| ≤ 1e-6** ister (`tests/test_reference_statsmodels.py`; test yalnızca CSV'yi okur).
- **Üretim:** `oracle/generate_reference_statsmodels.py` (motoru içe aktarmaz). İlk satır `#` başlık yorumu,
  sürümleri içerir: statsmodels 0.15.0, scipy 1.17.1, numpy 2.4.6, pandas 2.2.3. Bu makinede Smart App
  Control proje `.venv`'indeki pandas 3.0.6 DLL'lerini engellediği için tablo **ayrı geçici bir venv'de**
  (`pip install statsmodels==0.15.0 pandas==2.2.3`) üretildi; proje `.venv`'i değiştirilmedi.
- **Uyuşmazlıklar (test gevşetilmedi):**
  - **V13** (iki kuyruk, dz=5, α=0.05, güç=0.99): `solve_power` uyarısız 2.7243… döndürüyor, ama statsmodels'ın
    kendi `power` fonksiyonu bu N'de 0.913 veriyor (hedefin altında; kök değil). statsmodels N=3'te 0.975,
    N=4'te 0.99997 veriyor; tavan 3 ≠ motor 4. G*Power da N=4 (V13.png). statsmodels çözücüsünün sorunu.
  - **V16** (iki kuyruk, dz=0.5, α=0.05, güç=0.05 = α): `solve_power` yakınsamıyor (ConvergenceWarning, NaN).
    G*Power N=2 (V16.png).
  - İkisi de testte `pytest.mark.xfail(strict=True)` ile işaretlidir; CSV ve test ölçütü değişmedi. statsmodels
    bir gün doğru sonucu verirse test XPASS olur ve strict olduğu için kırmızıya döner.
- **Not:** V42'de (dz=0.00001) statsmodels motorla aynı N'yi (78488605096) veriyor, G*Power'dan farklı
  (LEDGER L17, Q7). İkisi de scipy'nin merkezsiz t'sini kullandığı için bu bağımsız bir doğrulama sayılmaz.
