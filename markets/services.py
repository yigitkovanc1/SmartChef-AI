import requests
import re
import math  # Yukarı yuvarlama işlemleri için


def migros_maliyet_hesapla(ai_malzemeler_listesi):
    hesaplanmis_malzemeler = []
    toplam_tarif_maliyeti = 0
    toplam_sepet_maliyeti = 0

    # 1. BEDAVA OLAN VEYA ARANMAYACAK MALZEMELER
    yoksayilacaklar = ["su", "sıcak su", "soğuk su", "musluk suyu", "buz", "kaynar su", "Ilık Su"]

    # 2. YANLIŞ ANLAŞILAN KELİMELERİ MİGROS'UN ANLAYACAĞI DİLE ÇEVİRME
    kelime_sozlugu = {
        "sıvı yağ": "Migros Ayçiçek Yağı 5 L",
        "ayçiçek yağı": "Migros Ayçiçek Yağı 5 L",
        "un": "sinangil buğday unu",
        "toz şeker": "ırmak toz şeker",
        "şeker": "ırmak toz şeker",
        "tuz": "billur tuz iyotlu",
        "süt": "içim tam yağlı süt",
        "tereyağı": "sütaş tereyağı",
        "yumurta": "keskinoglu 15'li l büyük boy yumurta",
        "yumurta sarısı": "keskinoglu 15'li l büyük boy yumurta",
        "yumurta akı": "keskinoglu 15'li l büyük boy yumurta",
        "süt": "migros uht süt 1 l",
        "vanilya": "dr.oetker şekerli vanilin",
        "süt kreması": "tikveşli krema",
        "süt kreması (karamel i̇çin)": "tikveşli krema",
        "krema": "tikveşli krema",
        "yoğurt": "Sütaş Kaymaksız Yoğurt 1000 G",
        "kabartma tozu": "dr.oetker kabartma tozu",
        "şekerli vanilin": "dr.oetker şekerli vanilin",
        "kakao": "dr.oetker kakao",
        "kuru maya": "dr.oetker kuru maya",
        "yaş maya": "pakmaya yaş maya",
        "Kedidili Bisküvi": "Balocco Savoiardı 200 G",
        "kedi dili": "Balocco Savoiardı 200 G",
        "kıyma": "uzman kasap dana kıyma",
        "dana kıyma": "uzman kasap dana kıyma",
        "tavuk göğsü": "banvit piliç göğüs",
        "sucuk": "şahin dana sucuk",
        "sosis": "pınar sosis",
        "tavuk göğüs": "piliç bonfile",
        "kemiksiz tavuk göğsü": "piliç bonfile",
        "kuşbaşı tavuk": "piliç sote",
        "tavuk kalça": "piliç incik",
        "salça": "tat domates salçası",
        "domates salçası": "tat domates salçası",
        "makarna": "filiz makarna",
        "pirinç": "yayla osmancık pirinç",
        "karabiber": "bağdat karabiber",
        "pul biber": "bağdat pul biber",
        "nane": "bağdat nane",
        "pide": "lavaş",
        "biber": "çarliston biber",
        "yeşil biber": "çarliston biber",
        "sarımsak": "kuru sarımsak file",
        "diş sarımsak": "kuru sarımsak file",
        "baş sarımsak": "kuru sarımsak file",
    }

    birim_ceviri_sozlugu = {
        "çay kaşığı": {"carpan": 5, "yeni_birim": "gr"},
        "tatlı kaşığı": {"carpan": 10, "yeni_birim": "gr"},
        "yemek kaşığı": {"carpan": 15, "yeni_birim": "gr"},
        "su bardağı": {"carpan": 200, "yeni_birim": "gr"},
        "çay bardağı": {"carpan": 100, "yeni_birim": "gr"},
        "fincan": {"carpan": 50, "yeni_birim": "gr"},
        "tutam": {"carpan": 2, "yeni_birim": "gr"},
        "dilim": {"carpan": 30, "yeni_birim": "gr"},
        "diş": {"carpan": 5, "yeni_birim": "gr"}
    }

    for malz in ai_malzemeler_listesi:
        orijinal_isim = malz.get('isim', '').strip().lower()
        ai_miktar = float(malz.get('miktar', 1))
        ai_birim = malz.get('birim', '').lower().strip()

        if orijinal_isim in yoksayilacaklar:
            hesaplanmis_malzemeler.append({
                "isim": malz.get('isim', ''),
                "market_isim": "Musluk Suyu (Bedava)",
                "sepet_fiyat": 0.0,
                "tarif_maliyet": 0.0,
                "bulundu": True
            })
            continue

        # ========================================================
        # 1. ZIRH: Yapay Zekanın Birimlerini Düzeltme
        # ========================================================
        for eski_birim, donusum in birim_ceviri_sozlugu.items():
            if eski_birim in ai_birim:
                ai_miktar = ai_miktar * donusum["carpan"]
                ai_birim = donusum["yeni_birim"]
                break

        aranan_kelime = kelime_sozlugu.get(orijinal_isim, orijinal_isim)

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

                        # Başlangıç değerleri (Gramaj bulunamazsa 1 paket sayarız)
                        tarif_maliyeti = market_fiyat
                        sepet_maliyeti = market_fiyat
                        kac_paket_lazim = 1

                        market_miktar = None
                        market_birim = None

                        # ========================================================
                        # 2. ZIRH: MARKET İSMİNDEN GRAMAJ AYIKLAMA (YENİLENDİ!)
                        # ========================================================
                        # Önce normal rakamlı olanları ara (Örn: 5 L, 500 G, 15 Adet)
                        match = re.search(r'(\d+[\.,]?\d*)\s*(G|KG|ML|L|ADET)\b', market_isim, re.IGNORECASE)
                        if match:
                            market_miktar = float(match.group(1).replace(',', '.'))
                            market_birim = match.group(2).lower()
                        else:
                            # EĞER RAKAM YOKSA: Sadece "Kg" veya "L" yazıyorsa 1 Kilo/1 Litre say!
                            match_tek = re.search(r'\b(KG|L)\b', market_isim, re.IGNORECASE)
                            if match_tek:
                                market_miktar = 1.0
                                market_birim = match_tek.group(1).lower()

                        # Eğer başarıyla gramaj bulabildiysek matematiği yapalım
                        if market_miktar and market_birim:
                            if market_birim == 'kg':
                                market_miktar *= 1000
                                market_birim = 'gr'
                            elif market_birim == 'l':
                                market_miktar *= 1000
                                market_birim = 'ml'
                            elif market_birim == 'g':
                                market_birim = 'gr'

                            # 3. ZIRH: MANAV KRİZİ (Adet vs Gr)
                            if ai_birim == "adet" and market_birim == "gr":
                                ai_miktar = ai_miktar * 150
                                ai_birim = "gr"

                            # 4. ZIRH: Katı/Sıvı Uyum Kalkanı
                            uyumlu_birimler = ["gr", "ml"]
                            birim_uyusuyor = (market_birim == ai_birim) or (
                                        market_birim in uyumlu_birimler and ai_birim in uyumlu_birimler)

                            if birim_uyusuyor and market_miktar > 0:
                                birim_fiyat = market_fiyat / market_miktar
                                tarif_maliyeti = birim_fiyat * ai_miktar
                                kac_paket_lazim = math.ceil(ai_miktar / market_miktar)
                                sepet_maliyeti = market_fiyat * kac_paket_lazim

                        toplam_sepet_maliyeti += sepet_maliyeti
                        toplam_tarif_maliyeti += tarif_maliyeti

                        gosterilecek_isim = market_isim if kac_paket_lazim == 1 else f"{market_isim} (x{kac_paket_lazim})"

                        hesaplanmis_malzemeler.append({
                            "isim": malz.get('isim', ''),
                            "market_isim": gosterilecek_isim,
                            "sepet_fiyat": round(sepet_maliyeti, 2),
                            "tarif_maliyet": round(tarif_maliyeti, 2),
                            "bulundu": True
                        })
                        continue

        except Exception as e:
            print(f"Migros Bot Hatası ({aranan_kelime}): {e}")

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