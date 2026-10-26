# AGENT COST & TELEMETRY

Bu belge, sprint boyunca kullanılan yapay zeka ajanının oturum sürelerini, token kullanımlarını ve maliyet tahminlerini takip eder.

## Oturum Metrikleri

| Oturum | Amaç | Kullanılan Model | Tahmini Giriş Token | Tahmini Çıkış Token | Araç Çağrısı Sayısı | Yaklaşık Süre |
|---|---|---|---|---|---|---|
| Sprint Kurulumu | Mimari, İskelet, CSV Şablonu, SPEC | Gemini Flash | 15,000 | 8,000 | 12 | ~4 dk |
| Oturum 1 (İnceleme) | Sayısal kararsızlık & scipy sol kuyruk analizi | Gemini Flash | 8,000 | 4,000 | 8 | ~3 dk |
| Oturum 2 (Yazım) | TDD Motor + CLI Geliştirme | Gemini Flash | 12,000 | 7,000 | 14 | ~4 dk |
| Oturum 3 (Doğrulama) | Self-check (kâhin değil): motorun aynı algoritmanın scipy kopyasıyla tutarlılığı; G*Power'a karşı ölçülmedi | Gemini Flash | 10,000 | 5,000 | 10 | ~3 dk |
| Bonus Oturumu | MCP Sunucusu + Türkçe Ajan Döngüsü | - | - | - | - | Bekliyor |

> Not: Gemini Flash satırları **tahmini, önceki araç**; ölçüm değildir, olduğu gibi bırakıldı.

> Not: Önceki sürümde bu satır "Conformance (%98.36)" diyordu. O oran G*Power uyumunu değil,
> motorun kendi kopyasıyla uyumunu ölçüyordu (bkz. HALLUCINATIONS.md H04).

---

## Denetim ve Temizlik Turu (2026-10-20, Claude Code / Claude Opus 5.5)

| Adım | Amaç | Commit |
|---|---|---|
| Denetim | Salt okunur proje incelemesi ve rapor | — |
| Temizlik turu 1 | Uydurma verinin ayıklanması, LEDGER/HALLUCINATIONS, paketleme, doğrulama, CLI hata sözleşmesi | `d7b36b3`…`dde0864` |
| Temizlik turu 2 | CONTRACT_ASSUMED.md, takma adlar, JSON/ondalık sözleşmesi, kalan temizlik | `9d62840` ve sonrası |

**Gerçek maliyet (`/cost` çıktısı):**

- 2026-10-20 denetim ve temizlik turları: **ölçülmedi** (`/cost` çıktısı alınmadı).
- İnceleme oturumları (G*Power binary, oturum 1 ve 2): **ölçülmedi**.
- 2026-10-22 Claude Code oturumu (yazım oturumu: durum raporu, git geçmişi temizliği, README, statsmodels
  çapraz kontrolü, xfail işaretleri, HALLUCINATIONS H07–H09). Kullanıcının yapıştırdığı çıktının "Session"
  bloğu, aynen:

```text
Session

Total cost:            $6.48
Total duration (API):  19m 30s
Total duration (wall): 45m 45s
Total code changes:    531 lines added, 14 lines removed
Usage by model:
    claude-haiku-5-5:  1.4k input, 30 output, 0 cache read, 0 cache write ($0.0002)
     claude-opus-5-5:  2.8k input, 98.5k output, 13.5m cache read, 224.6k cache write ($6.48)
Prompt cache (main):   81 requests · 98% of input tokens from cache · no misses · warm (1h TTL, last activity 50s ago)
```

> Aynı ekrandaki "Last 24h" kullanım paneli bu makinedeki tüm oturumların payını gösterir; maliyet ölçümü
> değildir, inceleme maliyeti ondan türetilmedi.

---

## Token ve Maliyet Özeti
- **Oturumlar**: yukarıdaki Gemini tablosu (tahmini, önceki araç); 2026-10-20 denetim ve temizlik turları;
  inceleme oturumu 1 (`c5b7bad`) ve 2 (`0f99cf1`); 2026-10-22 yazım oturumu; 2026-10-25/26 bonus oturumu
  (aşağıda).
- **Toplam Token Harcaması**: ~69,000 token (tahmini, önceki araç: yalnızca Gemini satırlarının toplamı)
- **Birim Maliyet Referansı**: Gemini 1.5 Flash tarifesi (tahmini, önceki araç)
- **Ölçülen maliyet**: yalnızca 2026-10-22 Claude Code oturumu, $6.48 (yukarıdaki `/cost` çıktısı)
- **İnceleme ile yazımın ayrılığı (git ile doğrulanabilir)**: İnceleme oturumları ayrı oturumlardı ve yalnızca
  `LEDGER.md` ile `SPEC.md`'ye dokundu (`git show --stat c5b7bad 0f99cf1`). Motoru yazım oturumu bu [REA]
  satırlarına göre değiştirdi: L18–L21 kuralları `095f284`'te kodda kanıtlarıyla anıldı; L32/L33 girdi
  aralıkları önce kırmızı test (`063075d`), sonra motor (`818a9d6`) olarak eklendi. Eski Gemini dönemi notu
  kanıtsız olduğu için kaldırıldı.

---

## Bonus oturumu (2026-10-25/26, Claude Code / Claude Opus 5.5)

| Adım | İçerik | Commit |
|---|---|---|
| multireg-r2 | Beş mod; G*Power M01–M28 (22/22 sayısal), eğitmen vektörleri 5/5 | `9342247`…`e6506ef` |
| MCP sunucusu | `initialize` el sıkışması, `gpower-clone-mcp`, BOM düzeltmesi, Claude Code ile canlı bağlantı | `b816891`…`e152c15` |
| AI ajanı | Gemini + MCP istemcisi, değer kaynağı denetimi (§10), log (§8) | `65f411a`…`48bcf4f` |
| Ölçek ağı | statsmodels 516 vektör, 499/499 uyumlu; `FTestPower` takası bulundu (H12) | `94eed4c` |
| Sistem 1 ve değerlendirme | Sınıflandırıcı, 10 soruluk set (TR 10/10, EN 10/10), MCP–GUI token ölçümü | `f6308b8`…`40a9b59` |

İterasyon: her adım önce kırmızı test, sonra kod (yeşil), sonra belge; canlı denemelerde iki hata yakalandı
(H10 `--` ayıracı, H11 UTF-8 BOM) ve bir yanlış varsayım düzeltildi (H12).

**Ajanın kendi model maliyeti (ölçülen, Gemini `usageMetadata`, `gemini-3.5-flash-lite`, ücretsiz katman):**

| Çalıştırma | Giriş token | Çıkış token |
|---|---|---|
| Değerlendirme, MCP yolu, Türkçe (10 soru) | 18 685 | 1 192 |
| Değerlendirme, MCP yolu, İngilizce (10 soru) | 18 592 | 1 212 |
| Değerlendirme, GUI yolu (6 soru, ekran görüntüsüyle) | 7 555 | 27 |
| Demo videosu (5 senaryo, `logs/agent_calls.jsonl` ilk 4 satır) | yalnızca araç çağıran turlar loglandı | |

Ücretsiz katman kullanıldığı için para maliyeti $0. Ham sayılar: `eval/results/`, `logs/agent_calls.jsonl`.

**Claude Code oturumunun maliyeti:** _[`/cost` çıktısı eklenecek]_

**Neyi farklı yapardım:** Canlı istemciyle denemeyi (gerçek Claude Code, gerçek PowerShell) belgeyi yazmadan
önce yapardım; H10 ve H11 birim testlerin göremediği, yalnızca gerçek ortamda çıkan hatalardı. Bağımsız bir
kütüphaneyi kullanmadan önce kâhin vektörüyle sınamak (H12) baştan kural olmalıydı.