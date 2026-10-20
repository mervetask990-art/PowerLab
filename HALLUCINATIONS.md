# HALLUCINATIONS: Hallüsinasyon ve Yanılgı Defteri

Bu dosya, tersine mühendislik veya kodlama oturumlarında yapay zeka ajanının ürettiği yanlış varsayımları, bunların hangi test veya diferansiyel kâhin doğrulamasıyla yakalandığını ve nasıl düzeltildiğini belgeler.

---

## Hallüsinasyon Kayıtları

### H01: Normal Dağılım Yaklaşımı Tuzağı
- **İddia Edilen**: "Eşleştirilmiş t-testinde $N > 30$ ise noncentral-t yerine normal dağılım yaklaşımı ($Z_{\alpha} + Z_{\beta}$) kullanılır."
- **Yanılgı Kaynağı**: Standart ders kitaplarında büyük örneklem için $Z$ yaklaşımı önerilmesi.
- **Nasıl Yakalandı?**: Diferansiyel test (`test_differential.py` - V01 vektörü). Normal yaklaşım $N=53$ veya $53.4$ verirken, G\*Power tam olarak $N=54$ ve noncentral-t tabanlı serbestlik derecesi $\text{df}=53$ üretmiştir.
- **Düzeltme**: Kodda hiçbir $Z$ yaklaşımına yer verilmedi; tüm hesaplamalar eksiksiz `scipy.stats.nct` ile gerçekleştirildi.
- **Durum**: Çözüldü.

---

### H02: Tek Taraflı Çift Kuyruk Entegrasyonu (Sol Kuyruk İhmali)
- **İddia Edilen**: "Çift kuyrukta güç hesabı sadece sağ kuyruktur: $1 - \text{cdf}(t_{\text{crit}})$. Sol kuyruk ihmal edilebilir."
- **Yanılgı Kaynağı**: Büyük etki büyüklüklerinde sol kuyruğun ($P(T \le -t_{\text{crit}} | \delta)$) sıfıra çok yakın olması.
- **Nasıl Yakalandı?**: Çok küçük etki büyüklüğü sınır testlerinde ($d_z = 0.05$ veya $0.10$). Tek taraflı sağ kuyruk integrali alındığında G\*Power'ın bildirdiği `actual_power` ile $4$. basamaktan itibaren sapma gözlendi. G\*Power iki taraflı kuyruğu toplamaktadır: $[1 - F(t_{\text{crit}})] + F(-t_{\text{crit}})$.
- **Düzeltme**: `families/t_paired.py` içinde çift kuyruk için her iki alan toplanacak şekilde formül revize edildi.
- **Durum**: Çözüldü.

---

### H03: Sol Kuyruk İntegralinde Sayısal Kararsızlık (scipy NaN Tuzağı)
- **İddia Edilen**: "Çift kuyruk hesabı `right_tail + left_tail` doğrudan tüm $N$ değerlerinde çalışır."
- **Yanılgı Kaynağı**: Aşırı büyük örneklem veya $ncp > 20$ olduğunda $t_{\text{crit}}$ sol kuyruk integrali matematiksel olarak $10^{-30}$ olmasına rağmen `scipy.stats.nct.cdf(-t_crit, df, ncp)` fonksiyonunun sayısal taşma nedeniyle `NaN` üretmesi.
- **Nasıl Yakalandı?**: Diferansiyel testte `REF_0641` vektöründe ($N$ beklenen: 1461) ikili arama `NaN >= target_power` karşılaştırması `False` verdiği için sağa sapmış ve $N=83640$ bulunarak test kırmızıya düşmüştür.
- **Düzeltme**: `nct_power` içinde `math.isnan(left_tail)` koruması eklenerek `left_tail = 0.0` yapılmış, böylece eşleşme oranı %51.25'ten **%98.36'ya** fırlamıştır.
- **Durum**: Çözüldü.

---

### H04: Taslak Prompt Değerinin Kâhin Zannedilmesi Tuzağı
- **İddia Edilen**: "Prompt 2 örneğindeki `actual_power: 0.9531` değeri mutlak doğrudur."
- **Yanılgı Kaynağı**: Şartname taslağındaki sayısal örneğin körü körüne test beklentisine yazılması.
- **Nasıl Yakalandı?**: `test_cli_contract.py` çalıştırıldığında motorun $N=54, \text{df}=53, \text{ncp}=3.674235$ ile ürettiği değer $0.950212$ çıkmış ve test fail vermiştir. Matematiksel integral elle teyit edildiğinde $1 - F(2.005746; 53, 3.674235)$ değerinin tam olarak $0.950212$ olduğu, $0.9531$ değerinin ise tek kuyruk ($tails=1$) veya farklı bir yuvarlamadan kaldığı tespit edilmiştir.
- **Düzeltme**: Beklenen değer kurala uygun olarak $0.950212$ olarak güncellendi.
- **Durum**: Çözüldü.
