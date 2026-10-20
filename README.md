# PowerLab: G*Power Uyumlu İstatistiksel Güç Analizi ve Boyut Hesaplama Kütüphanesi

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Architecture](https://img.shields.io/badge/architecture-clean--room-green.svg)]()
[![Status](https://img.shields.io/badge/status-active--sprint-yellow.svg)]()

> **Önemli Not**: Bu proje eğitim amaçlı bir yazılım mühendisliği (YZM301) çalışmasıdır. "G*Power" adı bir ürün adı olarak kullanılmamış, yalnızca temiz oda diferansiyel test kâhinliği (oracle) referansı olarak alınmıştır.

---

## 1. Proje Durumu ve Katmanlar

- [x] **Katman 0: Repo İskeleti ve Kurulum** (SPEC, LEDGER, CSV şablonları, prompts)
- [ ] **Katman 1: Kâhin Vektörleri** (30 G*Power girdi şablonu hazır; beklenen değerler boş, ekran görüntüsü bekleniyor)
- [x] **Katman 2: Oturum 1 (İnceleme)** (`LEDGER.md` var; ancak henüz hiçbir [REA] kanıtı yok — tüm binary iddiaları [AJAN])
- [x] **Katman 3: Oturum 2 (Hesap Motoru & CLI)** (`src/powerlab/engine/`, `src/powerlab/cli.py`)
- [ ] **Katman 4: Diferansiyel Test & Doğrulama** (G*Power'a karşı ölçülmedi: 0 kâhin vektörü; yalnızca self-check var, bkz. `conformance.md`)
- [ ] **Katman 5 (Bonus): MCP Sunucusu & Türkçe Klinik Ajan** (taslak kod var: `src/powerlab/mcp_server.py`, `src/powerlab/agent/`; gerçek MCP el sıkışması yok, ajan kural tabanlı, benchmark ölçülmedi)

---

## 2. MCP Araç Şeması (Model Context Protocol)

Sunucu modülü: `src/powerlab/mcp_server.py`  
Protokol: Model Context Protocol (MCP) / JSON-RPC 2.0 (stdio)

| Araç Adı | Parametre | Tip | Zorunlu? | Açıklama |
|---|---|---|---|---|
| `power_analysis` | `test` | string | Evet | Test ailesi (`t-paired`, `t2-indep`, `anova-oneway`, `chi2-contingency`, `multireg-r2`) |
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
- **Ajan Çağrı Günlüğü**: `eval/agent_calls.jsonl`

### Token / Süre / Doğruluk Karşılaştırması: MCP Yolu vs. GUI Yolu

Henüz ölçülmedi.

### İnceleme Altındaki Binary Bilgileri
- **Yazılım**: G*Power 3.1.9.7 for Windows (32/64 bit)
- **SHA-256 Hash**: `(Kendi GPower.exe dosyanızın hash değerini ekleyin: Get-FileHash GPower.exe)`
- **Atıf (Citations)**:
  - Faul, F., Erdfelder, E., Lang, A.-G., & Buchner, A. (2007). *G*Power 3: A flexible statistical power analysis program for the social, behavioral, and biomedical sciences.* Behavior Research Methods, 39, 175-191.
  - Faul, F., Erdfelder, E., Buchner, A., & Lang, A.-G. (2009). *Statistical power analyses using G*Power 3.1: Tests for correlation and regression analyses.* Behavior Research Methods, 41, 1149-1160.

---

## 2. Mimari Yapı

```text
repo/
├── README.md              # En üstte durum, hash, atıf, Sommerville bağlantısı
├── SPEC.md                # Gherkin kabul kriterleri
├── LEDGER.md              # [DOK] / [REA] / [AJAN] kanıt defteri
├── HALLUCINATIONS.md      # Yakalanan ajan yanılgıları ve düzeltmeler
├── AGENT_COST.md          # Telemetri, token ve süre kayıtları
├── .gitignore             # GPower.exe, *.gzf, ghidra projeleri
├── prompts/
│   ├── 01_inceleme_oturumu.md
│   └── 02_yazim_oturumu.md
├── oracle/
│   ├── gpower_vectors.csv         # G*Power kâhin şablonu (30 girdi; beklenen değerler boş)
│   ├── screenshots/               # Ekran görüntüleri (henüz boş)
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
  `oracle/screenshots/` altında karşılık gelen ekran görüntüsü varsa doldurulur. Şu an tüm beklenen
  sütunlar boştur; `test_differential.py` bu durumda G*Power testini açıkça **atlar (skip)**.
- **`oracle/selfcheck_scipy.csv` kâhin değildir.** Motorla aynı algoritmanın (kesikli N araması +
  `scipy.stats.nct`) ayrı bir kopyasından üretilmiştir; yalnızca motorun kendi kendine tutarlılığını
  sınar. Buradaki eşleşme oranı G*Power uyumu hakkında bilgi vermez.
- `oracle/_dogrulanmamis/legacy_vectors.csv`: önceki sürümde "G*Power değeri" olarak yazılmış ama
  ekran görüntüsü olmayan V01–V04 değerleri. Hiçbir testte kullanılmaz.

---

## 3. CLI Kullanım Sözleşmesi

Komut adı: `powerlab`

### A Priori Örnek:
```bash
python -m powerlab.cli --test t-paired --mode a-priori --tails 2 --dz 0.5 --alpha 0.05 --power 0.95
```
**Çıktı (Tek satır JSON):**
```json
{"n":54,"n_total":54,"actual_power":0.953103,"critical":2.005746,"df":53,"ncp":3.674235}
```

### Hata Durumu:
```bash
python -m powerlab.cli --test t-paired --mode a-priori --tails 2 --dz -0.5 --alpha 0.05 --power 0.95
```
**Çıktı (Çıkış kodu $\ne 0$):**
```json
{"error":"Invalid effect size: dz must be strictly positive (> 0)"}
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
