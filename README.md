# PowerLab: İstatistiksel Güç Analizi ve Örneklem Boyutu Hesaplama Kütüphanesi

> G*Power 3.1.9.7 davranışını referans alan bağımsız bir yeniden yazım; G*Power değildir.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Architecture](https://img.shields.io/badge/architecture-clean--room-green.svg)]()
[![Status](https://img.shields.io/badge/status-active--sprint-yellow.svg)]()

> **Önemli Not**: Bu proje eğitim amaçlı bir yazılım mühendisliği (YZM301) çalışmasıdır. "G*Power" adı bir ürün adı olarak kullanılmamış, yalnızca temiz oda diferansiyel test kâhinliği (oracle) referansı olarak alınmıştır.

---

## 1. Proje Durumu ve Katmanlar

- [x] **Katman 0: Repo İskeleti ve Kurulum** (SPEC, LEDGER, CSV şablonları, prompts)
- [ ] **Katman 1: Kâhin Vektörleri** (41 planlı vektörün 41'inin de ekran görüntüsü var; 37'sinde beklenen değer dolu, 4'ü G*Power hata kutusu (V17, V25, V29, V40). Diferansiyel test 33/37. Uyuşmazlıklar: motor dz ≤ 0'ı reddediyor, G*Power hesap yapıyor (V21, V26, V37, V41; LEDGER L13, L16); G*Power güç < α'yı (V17, L12) ve post hoc N=2'yi (V29, L15) reddediyor, motor reddetmiyor. Bkz. `oracle/TOPLAMA_LISTESI.md`)
- [x] **Katman 2: Oturum 1 (İnceleme)** (`LEDGER.md` var; ancak henüz hiçbir [REA] kanıtı yok — tüm binary iddiaları [AJAN])
- [x] **Katman 3: Oturum 2 (Hesap Motoru & CLI)** (`src/powerlab/engine/`, `src/powerlab/cli.py`)
- [ ] **Katman 4: Diferansiyel Test & Doğrulama** (G*Power'a karşı ölçülmedi: 0 kâhin vektörü; yalnızca self-check var, bkz. `conformance.md`)
- [ ] **Katman 5 (Bonus): MCP Sunucusu & Türkçe Klinik Ajan** (taslak kod var: `src/powerlab/mcp_server.py`, `src/powerlab/agent/`; gerçek MCP el sıkışması yok, ajan kural tabanlı, benchmark ölçülmedi)

---

## Kurulum (Windows)

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
gpower-clone --help
pytest
```

Birincil komut `gpower-clone`, ikinci komut `powerlab`; ikisi de aynı CLI'yi çalıştırır (bkz. `prompts/NOTLAR.md`).

---

## 2. MCP Araç Şeması (Model Context Protocol)

Sunucu modülü: `src/powerlab/mcp_server.py`  
Protokol: Model Context Protocol (MCP) / JSON-RPC 2.0 (stdio)

| Araç Adı | Parametre | Tip | Zorunlu? | Açıklama |
|---|---|---|---|---|
| `power_analysis` | `test` | string | Evet | Test ailesi: şimdilik yalnızca `t-paired` (multireg-r2 eklenince genişletilecek) |
| `power_analysis` | `mode` | string | Hayır | `a-priori` (varsayılan) veya `post-hoc` |
| `power_analysis` | `tails` | integer | Hayır | 1 (tek yönlü) veya 2 (çift yönlü, varsayılan: 2) |
| `power_analysis` | `dz` / `d` | number | Evet | Etki büyüklüğü ($d_z > 0$) |
| `power_analysis` | `alpha` | number | Evet | Anlamlılık düzeyi $\alpha \in (0, 1)$ |
| `power_analysis` | `power` | number | A-priori için | Hedef istatistiksel güç $1 - \beta \in (0, 1)$ |
| `power_analysis` | `n` | integer | Post-hoc için | Örneklem çift sayısı ($N \ge 2$) |
| `power_analysis` | `ratio` | number | Hayır | Bağımsız gruplarda $n_2/n_1$ oranı |

---

## 3. Türkçe Akıllı Klinik Ajan ve Benchmark (Bonus)

Ajan modülü: `src/powerlab/agent/clinical_agent.py`  
Benchmark çalıştırıcısı: `python eval/evaluate_agent.py`

### Benchmark Sonuçları (10 Klinik Soru):
- **Henüz ölçülmedi.** Beklenen etiketler ve `expected_n` değerleri ajanla aynı oturumda yazıldı ve hiçbir kâhinle doğrulanmadı.
- **Ajan Çağrı Günlüğü**: `eval/agent_calls.jsonl` (eski, geçersiz çalıştırma: `eval/_eski/`)

### Token / Süre / Doğruluk Karşılaştırması: MCP Yolu vs. GUI Yolu

Henüz ölçülmedi.

### İnceleme Altındaki Binary Bilgileri
- **Yazılım**: G*Power 3.1.9.7 for Windows (taşınabilir paket `GPowerWin_3.1.9.7`, kurulum gerektirmez)
- **Asıl çalıştırılan exe**: `GPowerNT.exe` (paketteki tek G*Power programı; repoya eklenmez)
- **Sürüm (dosya özellikleri)**: FileVersion / ProductVersion `3.1.9.7`, ProductName `GPower`, Company `Franz Faul`
- **Boyut**: 2.287.616 bayt
- **Mimari**: **32-bit (x86)**. PE başlığı: Machine `0x014C` (i386), Optional Header magic `0x10B` (PE32)
- **SHA-256 Hash**: `c63e6a133eb6372932f810c08cc33dc35a06d1ddb658f897bd6c34a754efc812`
  (`certutil -hashfile GPowerNT.exe SHA256` ve `Get-FileHash` ile aynı sonuç alındı)
- **Paketteki diğer dosya**: `VC_redist.x86.exe`, Microsoft Visual C++ 2015-2022 Redistributable (x86)
  14.36.32532; 13.837.672 bayt; SHA-256 `5365a927487945ecb040e143ea770adbb296074ece4021b1d14213bde538c490`.
  Çalışma zamanı kütüphanesidir, inceleme hedefi değildir.
- **Atıf (Citations)**:
  - Faul, F., Erdfelder, E., Lang, A.-G., & Buchner, A. (2007). *G*Power 3: A flexible statistical power analysis program for the social, behavioral, and biomedical sciences.* Behavior Research Methods, 39, 175-191.
  - Faul, F., Erdfelder, E., Buchner, A., & Lang, A.-G. (2009). *Statistical power analyses using G*Power 3.1: Tests for correlation and regression analyses.* Behavior Research Methods, 41, 1149-1160.

---

## 2. Mimari Yapı

```text
repo/
├── README.md              # En üstte durum, hash, atıf, Sommerville bağlantısı
├── SPEC.md                # Gherkin kabul kriterleri
├── CONTRACT_ASSUMED.md    # Varsayılan CLI sözleşmesi (resmi CONTRACT.md gelene kadar)
├── CLAUDE.md              # Ajan çalışma kuralları
├── LEDGER.md              # [DOK] / [REA] / [AJAN] kanıt defteri
├── HALLUCINATIONS.md      # Yakalanan ajan yanılgıları ve düzeltmeler
├── AGENT_COST.md          # Telemetri, token ve süre kayıtları
├── .gitignore             # GPower.exe, *.gzf, ghidra projeleri
├── pyproject.toml         # Paketleme; konsol komutları gpower-clone ve powerlab
├── prompts/
│   ├── 01_inceleme_oturumu.md
│   ├── 02_yazim_oturumu.md
│   └── NOTLAR.md              # Sonradan alınan kararlar (orijinal prompt'lar değiştirilmez)
├── oracle/
│   ├── gpower_vectors.csv         # G*Power kâhini: 41 vektör (41'i görüntülü, 37'si dolu)
│   ├── TOPLAMA_LISTESI.md         # G*Power'da girilecek vektörlerin yazdırılabilir kontrol listesi
│   ├── generate_toplama_listesi.py
│   ├── screenshots/               # G*Power ekran görüntüleri (Vxx.png)
│   ├── selfcheck_scipy.csv        # KÂHİN DEĞİL: motorun kendi kendine tutarlılık verisi
│   ├── generate_selfcheck_scipy.py
│   ├── boundary_vectors.csv       # Sınır değerler
│   └── _dogrulanmamis/
│       └── legacy_vectors.csv     # Ekran görüntüsü olmayan eski V01–V04 değerleri (kâhin değil)
├── src/
│   └── powerlab/
│       ├── engine/                # TEK hesap motoru (saf fonksiyonlar)
│       │   ├── distributions.py   # nct sarmalayıcıları
│       │   ├── solver.py          # N arama + durma koşulu
│       │   ├── rounding.py        # Tamsayı tavan yuvarlama
│       │   ├── validation.py      # Geçersiz girdi kuralları
│       │   └── families/
│       │       └── t_paired.py    # Eşleştirilmiş t-testi
│       ├── cli.py                 # İnce katman: argparse -> engine -> JSON
│       ├── mcp_server.py          # İnce katman (bonus MCP)
│       └── agent/                 # Bonus Türkçe klinik soru ajanı
└── tests/
    ├── test_differential.py       # Oracle CSV'lerini koşar
    ├── test_boundaries.py
    ├── test_cli_contract.py
    ├── test_cli_mcp_parity.py
    └── report/conformance.md      # Otomatik üretilen uyum raporu
```

### Kâhin ve self-check ayrımı

- **Kâhin yalnızca G*Power'dır.** `oracle/gpower_vectors.csv` içindeki bir beklenen değer, ancak
  `oracle/screenshots/` altında karşılık gelen ekran görüntüsü varsa doldurulur. Şu an 41 vektörden
  **37'si** dolu (V17, V25, V29, V40 G*Power hata kutusu; görüntüler `oracle/screenshots/`). `test_differential.py` dolu vektörleri çalıştırır:
  N ve df tam, diğer alanlar CSV'deki basamak sayısına (V01'de 7) kadar eşleşmelidir. Hiç dolu vektör
  kalmazsa test açıkça **atlanır (skip)**.
- **`oracle/selfcheck_scipy.csv` kâhin değildir.** Motorla aynı algoritmanın (kesikli N araması +
  `scipy.stats.nct`) ayrı bir kopyasından üretilmiştir; yalnızca motorun kendi kendine tutarlılığını
  sınar. Buradaki eşleşme oranı G*Power uyumu hakkında bilgi vermez.
- `oracle/_dogrulanmamis/legacy_vectors.csv`: önceki sürümde "G*Power değeri" olarak yazılmış ama
  ekran görüntüsü olmayan V01–V04 değerleri. Hiçbir testte kullanılmaz.

---

## 3. CLI Kullanım Sözleşmesi

Komut adı: `gpower-clone` (birincil), `powerlab` (ikincil). Kurulum yapılmadan `python -m powerlab.cli` de aynı CLI'yi çalıştırır.

### Çıktı, hata ve takma ad kuralları

Tüm kurallar ve gerekçeleri tek kaynakta: **[`CONTRACT_ASSUMED.md`](CONTRACT_ASSUMED.md)** (resmi CONTRACT.md gelince güncellenecek).

### A Priori Örnek:
```bash
gpower-clone --test t-paired --mode a-priori --tails 2 --dz 0.5 --alpha 0.05 --power 0.95
```
**Çıktı (Tek satır JSON):**
```json
{"n":54,"n_total":54,"actual_power":0.950212,"critical":2.005746,"df":53,"ncp":3.6742346}
```
> Motor çıktısıdır, kâhin değildir; değerler 7 ondalığa yuvarlanır. G*Power aynı girdilerde N=54, Df=53, δ=3.6742346, Critical t=2.0057460, Actual power=0.9502120 gösteriyor (`oracle/screenshots/V01.png`). JSON sondaki sıfırları atar (`2.0057460` → `2.005746`); değer aynıdır (CONTRACT_ASSUMED D3).

### Hata Durumu:
```bash
gpower-clone --test t-paired --mode a-priori --tails 2 --dz -0.5 --alpha 0.05 --power 0.95
```
**Çıktı (stdout, çıkış kodu 1):**
```json
{"error":"Etki b\u00fcy\u00fckl\u00fc\u011f\u00fc (dz) kesinlikle pozitif (> 0) olmal\u0131d\u0131r, al\u0131nan: -0.5"}
```

```bash
gpower-clone --test t-paired --tails 3 --alpha 0.05
```
**Çıktı (stdout, çıkış kodu 2):**
```json
{"error":"Ge\u00e7ersiz arg\u00fcman: argument --tails: invalid choice: 3 (choose from 1, 2)"}
```

---

## 4. Yazılım Mühendisliği & Sommerville Bağlantısı (Sınav Notları)

1. **Doğrulama (Verification) vs. Geçerleme (Validation)**:
   - *Verification ("Did we build the system right?")*: Motorun `SPEC.md` matematiksel tanımına ve test senaryolarına tam uygun çalıştığının birim testlerle (`pytest`) kanıtlanması.
   - *Validation ("Did we build the right system?")*: Motorun gerçek dünyadaki referans kâhin (G*Power GUI) ile diferansiyel olarak karşılaştırılıp en az %90 uyum kapısını geçtiğinin doğrulanması.
2. **Sınır Değer Analizi (Boundary Value Testing)**:
   - Aşırı küçük ($d_z = 0.01$), aşırı büyük ($d_z = 5.0$), sınır alfa ($\alpha \to 0$), sınır güç ($\text{power} \le \alpha$) durumlarının incelenmesi.
3. **Test Güdümlü Geliştirme (TDD)**:
   - Önce SPEC senaryolarının kırmızı testler olarak yazılması, ardından motor fonksiyonlarının yazılarak yeşile çevrilmesi.
4. **Temiz Oda (Clean Room) Yazılım Mühendisliği**:
   - İnceleme oturumu (analiz / REA) ile yazım oturumunun (uygulama) ayrılması; kod geliştiriciye yalnızca davranışsal şartnamenin verilmesi.
5. **Konfigürasyon Yönetimi & İzlenebilirlik**:
   - Her kabul kriteri (`SPEC.md`), kanıt kaydı (`LEDGER.md`), kâhin vektörü (`oracle/`) ve birim test arasında çift yönlü izlenebilirlik ($V01 \to L06 \to \text{test\_differential}$).
