# AGENT COST & TELEMETRY

Bu belge, sprint boyunca kullanılan yapay zeka ajanının oturum sürelerini, token kullanımlarını ve maliyet tahminlerini takip eder.

## Oturum Metrikleri

| Oturum | Amaç | Kullanılan Model | Tahmini Giriş Token | Tahmini Çıkış Token | Araç Çağrısı Sayısı | Yaklaşık Süre |
|---|---|---|---|---|---|---|
| Sprint Kurulumu | Mimari, İskelet, CSV Şablonu, SPEC | Gemini Flash | 15,000 | 8,000 | 12 | ~4 dk |
| Oturum 1 (İnceleme) | Sayısal kararsızlık & scipy sol kuyruk analizi | Gemini Flash | 8,000 | 4,000 | 8 | ~3 dk |
| Oturum 2 (Yazım) | TDD Motor + CLI Geliştirme | Gemini Flash | 12,000 | 7,000 | 14 | ~4 dk |
| Oturum 3 (Doğrulama) | Diferansiyel Test & Conformance (%98.36) | Gemini Flash | 10,000 | 5,000 | 10 | ~3 dk |
| Bonus Oturumu | MCP Sunucusu + Türkçe Ajan Döngüsü | - | - | - | - | Bekliyor |

---

## Token ve Maliyet Özeti
- **Toplam Oturum**: 4 / 5 tamamlandı
- **Toplam Token Harcaması**: ~69,000 token
- **Birim Maliyet Referansı**: Gemini 1.5 Flash tarifesi
- **Maliyet Verimliliği Notu**: REA incelemesi ile kod yazımı tamamen birbirinden ayrılmış ("Clean Room"), sayısal uç anomaliler (sol kuyruk NaN tuzağı) hızla izole edilerek context kirliliği engellenmiştir.
