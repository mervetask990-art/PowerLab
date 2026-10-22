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
  çapraz kontrolü, xfail işaretleri, HALLUCINATIONS H07–H09). Kullanıcının yapıştırdığı çıktı, aynen:

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

Current session · Resets 2:30pm (Europe/Istanbul)
████████████████████▉                                 
36% used

Current week (all models) · Resets Oct 29, 4am (Europe/Istanbul)
██▉                                                   
5% used

What's contributing to your limits usage?
Approximate · sessions on this machine only

Last 24h · shares overlap

89%  Start fresh when you switch tasks · run /clear
14%  See what fills your context · run /context
11%  Run /reverse-engineer-anything on a cheaper model

Skills                  % of usage
/reverse-engineer-anything     11%

MCP servers             % of usage
rea                             7%

f to fix 1 of 3 · d to day · w to week

Usage credits
Usage credits are off · /usage-credits to turn them on

Esc to cancel
```

> "Last 24h" bölümü bu makinedeki tüm oturumların kullanım payıdır (/reverse-engineer-anything ve rea
> satırları inceleme oturumlarından gelebilir); bir maliyet ölçümü değildir, inceleme maliyeti buradan
> türetilmedi.

---

## Token ve Maliyet Özeti
- **Toplam Oturum**: 4 / 5 tamamlandı
- **Toplam Token Harcaması**: ~69,000 token (tahmini, önceki araç: yalnızca Gemini satırlarının toplamı)
- **Birim Maliyet Referansı**: Gemini 1.5 Flash tarifesi (tahmini, önceki araç)
- **Ölçülen maliyet**: yalnızca 2026-10-22 Claude Code oturumu, $6.48 (yukarıdaki `/cost` çıktısı)
- **Maliyet Verimliliği Notu**: REA incelemesi ile kod yazımı tamamen birbirinden ayrılmış ("Clean Room"), sayısal uç anomaliler (sol kuyruk NaN tuzağı) hızla izole edilerek context kirliliği engellenmiştir.
