import requests
import re

def migros_maliyet_hesapla(ai_malzemeler_listesi):
    hesaplanmis_malzemeler = []
    toplam_tarif_maliyeti = 0
    toplam_sepet_maliyeti = 0

    # 1. BEDAVA OLAN VEYA ARANMAYACAK MALZEMELER
    yoksayilacaklar = ["su", "sıcak su", "soğuk su", "musluk suyu", "buz", "kaynar su"]

    # 2. YANLIŞ ANLAŞILAN KELİMELERİ MİGROS'UN ANLAYACAĞI DİLE ÇEVİRME
    kelime_sozlugu = {
        "tuz": "billur tuz",  # Bulaşık makinesi tuzu bulmasın diye
        "şeker": "toz şeker",
        "yağ": "sıvı yağ",
        "un": "buğday unu"
    }

    # BÜTÜN İŞLEMİ TEK DÖNGÜDE YAPIYORUZ
    for malz in ai_malzemeler_listesi:
        orijinal_isim = malz.get('isim', '').strip().lower()
        ai_miktar = float(malz.get('miktar', 1))
        ai_birim = malz.get('birim', '').lower().strip()  # gr, ml, adet

        # --- AŞAMA 1: BEDAVA KONTROLÜ ---
        if orijinal_isim in yoksayilacaklar:
            hesaplanmis_malzemeler.append({
                "isim": malz.get('isim', ''),
                "market_isim": "Musluk Suyu (Bedava)",
                "sepet_fiyat": 0.0,
                "tarif_maliyet": 0.0,
                "bulundu": True
            })
            continue  # Suysa bunu listeye ekle ve MİGROSA GİTMEDEN sıradaki malzemeye geç!

        # --- AŞAMA 2: SÖZLÜK FİLTRESİ ---
        # Kelime sözlükte varsa yenisini al, yoksa orijinaliyle devam et
        aranan_kelime = kelime_sozlugu.get(orijinal_isim, orijinal_isim)

        # --- AŞAMA 3: MİGROS'TA ARAMA (Filtrelenmiş kelime ile) ---
        url = "https://www.migros.com.tr/rest/search/screens/products"
        params = {"q": aranan_kelime}
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "tr",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "x-pwa": "true",
            "x-device-pwa": "true",
            "x-forwarded-rest": "true"
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=5)
            if response.status_code == 200:
                urunler = response.json().get('data', {}).get('searchInfo', {}).get('storeProductInfos', [])

                if urunler:
                    ilk_urun = urunler[0]
                    market_isim = ilk_urun.get('name', 'İsimsiz Ürün')
                    ham_fiyat = ilk_urun.get('salePrice', ilk_urun.get('regularPrice', 0))

                    if ham_fiyat != 0:
                        market_fiyat = ham_fiyat / 100
                        tarif_maliyeti = market_fiyat  # Başlangıçta tamamını sayıyoruz

                        # REGEX SİHRİ: Market isminden Gramaj/Litre yakalama (Örn: 570 G, 1 KG, 2.5 L)
                        match = re.search(r'(\d+[\.,]?\d*)\s*(G|KG|ML|L|ADET)', market_isim, re.IGNORECASE)

                        if match:
                            market_miktar = float(match.group(1).replace(',', '.'))
                            market_birim = match.group(2).lower()

                            # Market birimlerini standartlaştırma
                            if market_birim == 'kg':
                                market_miktar *= 1000
                                market_birim = 'gr'
                            elif market_birim == 'l':
                                market_miktar *= 1000
                                market_birim = 'ml'
                            elif market_birim == 'g':
                                market_birim = 'gr'

                            # PORSİYON HESAPLA!
                            if market_birim == ai_birim and market_miktar > 0:
                                birim_fiyat = market_fiyat / market_miktar
                                tarif_maliyeti = birim_fiyat * ai_miktar

                        toplam_sepet_maliyeti += market_fiyat
                        toplam_tarif_maliyeti += tarif_maliyeti

                        hesaplanmis_malzemeler.append({
                            "isim": malz.get('isim', ''),
                            "market_isim": market_isim,
                            "sepet_fiyat": round(market_fiyat, 2),
                            "tarif_maliyet": round(tarif_maliyeti, 2),
                            "bulundu": True
                        })
                        continue  # Başarılıysa döngüde sonrakine geç

        except Exception as e:
            print(f"Migros Bot Hatası ({aranan_kelime}): {e}")

        # Eğer API çökerse veya ürün hiç bulunamazsa
        hesaplanmis_malzemeler.append({
            "isim": malz.get('isim', ''),
            "bulundu": False
        })

    return {
        "durum": "basarili",
        "malzemeler": hesaplanmis_malzemeler,
        "toplam_sepet": round(toplam_sepet_maliyeti, 2),
        "toplam_tarif_maliyeti": round(toplam_tarif_maliyeti, 2)
    }


