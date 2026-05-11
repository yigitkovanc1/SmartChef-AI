import requests
import re
import math

def migros_maliyet_hesapla(ai_malzemeler_listesi):
    hesaplanmis_malzemeler = []
    toplam_tarif_maliyeti = 0
    toplam_sepet_maliyeti = 0

    # 1. BEDAVA OLAN VEYA ARANMAYACAK MALZEMELER
    yoksayilacaklar = ["su", "sıcak su", "soğuk su", "musluk suyu", "buz", "kaynar su", "ılık su"]

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
        "vanilya": "dr.oetker şekerli vanilin",
        "toz vanilya": "dr.oetker şekerli vanilin",
        "şekerli vanilin": "dr.oetker şekerli vanilin",
        "süt kreması": "tikveşli krema",
        "krema": "tikveşli krema",
        "yoğurt": "Sütaş Kaymaksız Yoğurt 1000 G",
        "kabartma tozu": "dr.oetker kabartma tozu",
        "kakao": "dr.oetker kakao",
        "kuru maya": "dr.oetker kuru maya",
        "yaş maya": "pakmaya yaş maya",
        "kedidili bisküvi": "Balocco Savoiardı 200 G",
        "kedi dili": "Balocco Savoiardı 200 G",
        "kıyma": "uzman kasap dana kıyma",
        "dana kıyma": "uzman kasap dana kıyma",
        "tavuk göğsü": "banvit piliç göğüs",
        "sucuk": "şahin dana sucuk",
        "sosis": "pınar sosis",
        "salça": "tat domates salçası",
        "domates salçası": "tat domates salçası",
        "makarna": "filiz makarna",
        "pirinç": "yayla osmancık pirinç",
        "karabiber": "bağdat karabiber",
        "pul biber": "bağdat pul biber",
        "kuru kekik": "Migros Kekik",
        "nane": "bağdat nane",
        "pide": "lavaş",
        "biber": "çarliston biber",
        "yeşil biber": "çarliston biber",
        "sarımsak": "kuru sarımsak file"
    }

    birim_ceviri_sozlugu = {
        "çay kaşığı": {"carpan": 5, "yeni_birim": "gr"},
        "tatlı kaşığı": {"carpan": 10, "yeni_birim": "gr"},
        "yemek kaşığı": {"carpan": 15, "yeni_birim": "gr"},
        "çorba kaşığı": {"carpan": 15, "yeni_birim": "gr"},
        "kahve kaşığı": {"carpan": 3, "yeni_birim": "gr"},
        "su bardağı": {"carpan": 200, "yeni_birim": "gr"},
        "çay bardağı": {"carpan": 100, "yeni_birim": "gr"},
        "kahve fincanı": {"carpan": 75, "yeni_birim": "gr"},
        "fincan": {"carpan": 50, "yeni_birim": "gr"},
        "kupa": {"carpan": 250, "yeni_birim": "gr"},
        "kase": {"carpan": 300, "yeni_birim": "gr"},
        "diş": {"carpan": 5, "yeni_birim": "gr"},
        "baş": {"carpan": 50, "yeni_birim": "gr"},
        "dilim": {"carpan": 30, "yeni_birim": "gr"},
        "parça": {"carpan": 50, "yeni_birim": "gr"},
        "yaprak": {"carpan": 2, "yeni_birim": "gr"},
        "dal": {"carpan": 5, "yeni_birim": "gr"},
        "kök": {"carpan": 20, "yeni_birim": "gr"},
        "tutam": {"carpan": 2, "yeni_birim": "gr"},
        "avuç": {"carpan": 30, "yeni_birim": "gr"},
        "kepçe": {"carpan": 100, "yeni_birim": "ml"},
        "damla": {"carpan": 1, "yeni_birim": "ml"},
        "fiske": {"carpan": 1, "yeni_birim": "gr"},
        "kilogram": {"carpan": 1000, "yeni_birim": "gr"},
        "kilo": {"carpan": 1000, "yeni_birim": "gr"},
        "kg": {"carpan": 1000, "yeni_birim": "gr"},
        "litre": {"carpan": 1000, "yeni_birim": "ml"},
        "lt": {"carpan": 1000, "yeni_birim": "ml"},
        "yarım kilo": {"carpan": 500, "yeni_birim": "gr"},
        "yarım litre": {"carpan": 500, "yeni_birim": "ml"},
        "çeyrek kilo": {"carpan": 250, "yeni_birim": "gr"},
        "paket": {"carpan": 1, "yeni_birim": "adet"},
        "kutu": {"carpan": 1, "yeni_birim": "adet"},
        "kavanoz": {"carpan": 1, "yeni_birim": "adet"},
        "şişe": {"carpan": 1, "yeni_birim": "adet"},
        "poşet": {"carpan": 1, "yeni_birim": "adet"}
    }

    adet_gramaj_sozlugu = {
        "soğan": 150, "domates": 150, "patates": 200, "patlıcan": 200, "kabak": 200,
        "havuç": 100, "limon": 100, "salatalık": 120, "biber": 30, "yeşil biber": 30,
        "kırmızı biber": 50, "çarliston": 30, "lavaş": 50, "pide": 200, "sarımsak": 5,
        "mantar": 20, "çilek": 15, "muz": 120, "elma": 150,
        "maydanoz": 50, "dereotu": 50, "nane": 50, "roka": 50, "marul": 300, "kıvırcık": 300,
        "yumurta": 50, "yumurta sarısı": 50, "yumurta akı": 50
    }

    # ====================================================================================
    # YENİ MİMARİ: DATA AGGREGATOR (KOPYA MALZEME BİRLEŞTİRİCİ ZIRH)
    # ====================================================================================
    birlestirilmis_dict = {}

    for malz in ai_malzemeler_listesi:
        orijinal_isim = malz.get('isim', '').strip().lower()
        ai_miktar = float(malz.get('miktar', 1))
        ai_birim = malz.get('birim', '').lower().strip()

        for eski_birim, donusum in birim_ceviri_sozlugu.items():
            if eski_birim in ai_birim:
                ai_miktar = ai_miktar * donusum["carpan"]
                ai_birim = donusum["yeni_birim"]
                break

        anahtar = f"{orijinal_isim}_{ai_birim}"

        if anahtar in birlestirilmis_dict:
            birlestirilmis_dict[anahtar]['miktar'] += ai_miktar
        else:
            birlestirilmis_dict[anahtar] = {
                "isim": malz.get('isim', ''),
                "orijinal_isim": orijinal_isim,
                "miktar": ai_miktar,
                "birim": ai_birim
            }

    ai_malzemeler_birlestirilmis = list(birlestirilmis_dict.values())

    # ====================================================================================
    # MİGROS BOTU BAŞLIYOR
    # ====================================================================================
    for malz in ai_malzemeler_birlestirilmis:
        orijinal_isim = malz['orijinal_isim']
        ai_miktar = malz['miktar']
        ai_birim = malz['birim']

        if orijinal_isim in yoksayilacaklar:
            hesaplanmis_malzemeler.append({
                "isim": malz.get('isim', ''),
                "market_isim": "Musluk Suyu (Bedava)",
                "sepet_fiyat": 0.0,
                "tarif_maliyet": 0.0,
                "bulundu": True
            })
            continue

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

                        tarif_maliyeti = market_fiyat
                        sepet_maliyeti = market_fiyat
                        kac_paket_lazim = 1

                        market_miktar = None
                        market_birim = None

                        # ========================================================
                        # 2. ZIRH: MARKET İSMİNDEN GRAMAJ AYIKLAMA
                        # ========================================================
                        match_coklu = re.search(r'(\d+)\s*\'*[l][ıiuü]\b', market_isim, re.IGNORECASE)
                        if match_coklu:
                            market_miktar = float(match_coklu.group(1))
                            market_birim = "adet"
                        else:
                            match = re.search(r'(\d+[\.,]?\d*)\s*(G|KG|ML|L|ADET|BAĞ|DEMET)\b', market_isim, re.IGNORECASE)
                            if match:
                                market_miktar = float(match.group(1).replace(',', '.'))
                                market_birim = match.group(2).lower()
                            else:
                                match_tek = re.search(r'\b(KG|L|ADET|BAĞ|DEMET)\b', market_isim, re.IGNORECASE)
                                if match_tek:
                                    market_miktar = 1.0
                                    market_birim = match_tek.group(1).lower()
                                else:
                                    market_miktar = 1.0
                                    market_birim = "adet"

                        # ========================================================
                        # 3. ZIRH: AKILLI MANAV KRİZİ VE MATEMATİK HESABI
                        # ========================================================
                        if market_miktar and market_birim:
                            if market_birim == 'kg':
                                market_miktar *= 1000
                                market_birim = 'gr'
                            elif market_birim == 'l':
                                market_miktar *= 1000
                                market_birim = 'ml'
                            elif market_birim == 'g':
                                market_birim = 'gr'
                            elif market_birim in ['bağ', 'demet']:
                                market_birim = 'adet'

                            ortalama_gramaj = 150
                            for kelime, gram in adet_gramaj_sozlugu.items():
                                if kelime in orijinal_isim:
                                    ortalama_gramaj = gram
                                    break

                            if ai_birim == "adet" and market_birim == "gr":
                                ai_miktar = ai_miktar * ortalama_gramaj
                                ai_birim = "gr"

                            elif ai_birim in ["gr", "ml"] and market_birim == "adet":
                                market_miktar = market_miktar * ortalama_gramaj
                                market_birim = ai_birim

                            uyumlu_birimler = ["gr", "ml"]
                            birim_uyusuyor = (market_birim == ai_birim) or (
                                        market_birim in uyumlu_birimler and ai_birim in uyumlu_birimler)

                            # MATEMATİĞİN ÇALIŞTIĞI ANA KALP BURASI:
                            if birim_uyusuyor and market_miktar > 0:
                                birim_fiyat = market_fiyat / market_miktar
                                tarif_maliyeti = birim_fiyat * ai_miktar
                                kac_paket_lazim = math.ceil(ai_miktar / market_miktar)
                                sepet_maliyeti = market_fiyat * kac_paket_lazim

                        # Toplamları güncelle
                        toplam_sepet_maliyeti += sepet_maliyeti
                        toplam_tarif_maliyeti += tarif_maliyeti

                        gosterilecek_isim = market_isim if kac_paket_lazim <= 1 else f"{market_isim} (x{kac_paket_lazim})"

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