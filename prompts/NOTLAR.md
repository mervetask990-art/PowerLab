# prompts/ notları

Bu klasördeki `01_inceleme_oturumu.md` ve `02_yazim_oturumu.md` dosyaları oturumların **ilk
prompt'larıdır** ve ödev gereği olduğu gibi bırakılmıştır. Sonradan alınan kararlar bu dosyada
tutulur.

## Komut adı çelişkisi: `powerlab` mı, `gpower-clone` mu?

- `02_yazim_oturumu.md` şöyle der: *"gpower-clone değil: komut adı "powerlab"."*
- Sonradan alınan karar (2026-10-20): **birincil konsol komutu `gpower-clone`** oldu, `powerlab`
  ikinci komut olarak kaldı. Paket adı `powerlab`.
- **Neden**: Dersin otomatik değerlendirme düzeneği CLI'yi `gpower-clone` adıyla çağırıyor. Komut
  adı bu düzeneğe uyması için seçildi; ürün adı olarak G*Power kullanılmıyor. Açıklama metinleri
  "G*Power 3.1.9.7 davranışını referans alan bağımsız bir yeniden yazım; G*Power değildir"
  ifadesini kullanır.
- Her iki komut da aynı giriş noktasını (`powerlab.cli:main`) çağırır; davranışları aynıdır.
