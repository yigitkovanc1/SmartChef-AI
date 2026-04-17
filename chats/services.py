import os
import json
from google import genai
from .models import Chat
from recipes.models import Recipe, Ingredient, RecipeIngredient
import difflib
import re


def benzer_tarif_bul(aranan_isim):
    """
    Regex kullanarak süs kelimelerini tamamen yok eder ve gelişmiş benzerlik taraması yapar.
    Kaşarlı Menemen ile Menemen'i ayırır, İskender ile İskender Kebap'ı bağlar.
    """
    if not aranan_isim:
        return None

    aranan_isim = aranan_isim.lower().strip()

    # 1. AŞAMA: Süs kelimelerini çöp kutusuna at
    silinecekler = r'\b(bana|bir|tarifi|tarif|tarifleri|yemeği|ev yapımı|kolay|pratik|lezzetli|nefis|klasik|orijinal|özel|usulü|nasıl|yapılır|istiyorum|ver)\b'
    temiz_isim = re.sub(silinecekler, '', aranan_isim).strip()
    temiz_isim = " ".join(temiz_isim.split())

    if not temiz_isim:
        return None

    tum_tarifler = Recipe.objects.all()

    # 2. AŞAMA: KESİN EŞLEŞME (Menemen = Menemen)
    # Önce birebir aynı ismi taşıyan var mı diye bakarız.
    for t in tum_tarifler:
        db_isim = t.title.lower().replace('*', '').strip()
        if db_isim == temiz_isim:
            return t

    # 3. AŞAMA: BAŞLANGIÇ VE BENZERLİK EŞLEŞMESİ (İskender = İskender Kebap)
    # Eğer kullanıcı "Menemen" yazdıysa, "Kaşarlı Menemen"in BAŞLANGICI "Menemen" olmadığı için onu es geçer!
    # Ama kullanıcı "İskender" yazdıysa, "İskender Kebap"ın BAŞLANGICI "İskender" olduğu için yakalar!
    for t in tum_tarifler:
        db_isim = t.title.lower().replace('*', '').strip()

        if db_isim.startswith(temiz_isim) or temiz_isim.startswith(db_isim):
            return t

        # Difflib ile %80 benzerlik ölçümü (Ufak harf hataları için: örn. Hmbürger)
        benzerlik_orani = difflib.SequenceMatcher(None, temiz_isim, db_isim).ratio()
        if benzerlik_orani >= 0.80:
            return t

    return None

def gemini_ile_sohbet_et(user, session_id, user_message):
    Chat.objects.create(user=user, session_id=session_id, message=user_message, sender='user')

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    # 🚀 PROMPT GÜNCELLENDİ: Kozmetik kalkanı ve net malzeme isimleri zorunluluğu getirildi!
    prompt = f"""
    Senin adın SmartChef. Dünyanın en iyi yapay zeka şefisin.
    Kullanıcı sana yapmak istediği bir yemeğin adını söyleyecek.

    ÇOK ÖNEMLİ KURALLAR:
    1. FORMAT KURALI: Cevabını KESİNLİKLE VE SADECE aşağıdaki JSON formatında vermelisin. Başka hiçbir metin ekleme.

    2. MARKET KURALI (ÇOK ÖNEMLİ): Kullanacağın tüm malzemeler standart bir Türk marketinde kolayca bulunabilen şeyler olmalı. Egzotik malzeme KESİNLİKLE KULLANMA. Malzeme isimlerinde asla genel ifadeler kullanma. Örneğin 'Sıvı Yağ' YERİNE KESİNLİKLE 'Ayçiçek Yağı' yaz. 'Kıyma' yerine 'Dana Kıyma' yaz. 'Pide' yerine 'Lavaş' yaz. Kozmetik ve temizlik ürünleri KESİNLİKLE önerme.

    3. İSİMLENDİRME VE BİRLEŞTİRME KURALI (EN ÖNEMLİSİ): 
    - Tarifin farklı aşamaları (hamur, sos, krema, üzeri vb.) için aynı malzemeden gerekiyorsa, bunları ASLA ayrı satırlarda listeleme! 
    - Miktarları kendi içinde topla ve TEK BİR KALEM olarak yaz. 
    - YANLIŞ KULLANIM: "Toz Şeker (Hamur için)" 100 gr, "Toz Şeker (Karamel için)" 50 gr.
    - DOĞRU KULLANIM: "Toz Şeker" 150 gr. 
    - Malzeme isimlerinin yanına ASLA parantez açıp (hamur için, sos için, süslemek için) gibi notlar DÜŞME!

    4. BİRİM KURALI: Miktar kısmına SADECE SAYI yaz. Birim kısmına KESİNLİKLE SADECE "gr", "ml" veya "adet" yaz. Çay kaşığı, su bardağı gibi ölçüler KULLANMA, bunları gr veya ml'ye çevir.

    {{
        "tarif_adi": "İskender Kebap",
        "kac_kisilik": 2,
        "sohbet": "İşte harika bir tarif... (Yapılış aşamaları)",
        "malzemeler": [
            {{"isim": "Dana Kontrfile", "miktar": 350, "birim": "gr"}},
            {{"isim": "Lavaş", "miktar": 1, "birim": "adet"}},
            {{"isim": "Tereyağı", "miktar": 75, "birim": "gr"}}
        ]
    }}

    Kullanıcının isteği: {user_message}
    """

    yeni_tarif_id = None

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )

        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:-3].strip()
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:-3].strip()

        try:
            ai_data = json.loads(raw_text, strict=False)
        except json.JSONDecodeError as decode_err:
            print(
                f"\n--- JSON ÇEVİRİ HATASI ---\nHATA: {decode_err}\nBOZUK METİN: {raw_text}\n--------------------------\n")
            ai_data = {}

        tarif_adi = ai_data.get("tarif_adi", "İsimsiz Tarif")
        kac_kisilik = ai_data.get("kac_kisilik", 1)  # YENİ: Kaç kişilik olduğunu JSON'dan çekiyoruz
        sohbet_metni = ai_data.get("sohbet", "İşte harika bir tarif şef!")
        malzemeler_listesi = ai_data.get("malzemeler", [])

        # YENİ: Sohbet metninin en başına porsiyon bilgisini havalı bir şekilde ekliyoruz
        sohbet_metni = f"🍽️ **Bu tarif {kac_kisilik} kişiliktir.**\n\n" + sohbet_metni

        # Veritabanı Kayıt İşlemleri
        if malzemeler_listesi:
            mevcut_tarif = benzer_tarif_bul(tarif_adi)

            if not mevcut_tarif:
                # 🚀 HATA DÜZELTİLDİ: request.user yerine sadece user yazıldı!
                yeni_tarif = Recipe.objects.create(
                    user=user,
                    title=tarif_adi,
                    instructions=sohbet_metni
                )
                yeni_tarif_id = str(yeni_tarif.id)

                for malz in malzemeler_listesi:
                    isim = malz.get("isim", "").lower().strip()
                    miktar = malz.get("miktar", 0)
                    birim = malz.get("birim", "")

                    if isim:
                        ingredient_obj, created = Ingredient.objects.get_or_create(name=isim)
                        RecipeIngredient.objects.create(
                            recipe=yeni_tarif,
                            ingredient=ingredient_obj,
                            quantity=miktar,
                            unit=birim
                        )
            else:
                yeni_tarif_id = str(mevcut_tarif.id)

    except Exception as e:
        sohbet_metni = "Üzgünüm şef, tarif defterimi bulamıyorum. Lütfen yemeğin adını tekrar yazar mısın?"
        malzemeler_listesi = []
        import traceback
        traceback.print_exc()  # Hatayı tam görelim

    db_kayit = sohbet_metni
    if malzemeler_listesi:
        db_kayit += "\n\nMalzemeler:\n- " + "\n- ".join(
            [f"{m.get('miktar')} {m.get('birim')} {m.get('isim')}" for m in malzemeler_listesi])

    Chat.objects.create(user=user, session_id=session_id, message=db_kayit, sender='ai')

    return {
        "sohbet": sohbet_metni,
        "malzemeler": [f"{m.get('miktar')} {m.get('birim')} {m.get('isim')}" for m in malzemeler_listesi],
        "recipe_id": yeni_tarif_id
    }