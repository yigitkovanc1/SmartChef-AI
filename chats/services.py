import os
import json
from google import genai
from .models import Chat
from recipes.models import Recipe, Ingredient, RecipeIngredient
import difflib


def benzer_tarif_bul(aranan_isim):
    """
    Girilen tarif ismini veritabanındakilerle karşılaştırıp %80'den
    fazla benzerlik varsa o tarifi döndürür.
    """
    aranan_isim = aranan_isim.lower().strip()

    # 1. AŞAMA: Süs Kelimelerini Temizle
    # (Yapay zeka "Nefis Ev Yapımı Hamburger Tarifi" derse sadece "hamburger" kalsın)
    gereksiz_kelimeler = ["tarifi", "ev yapımı", "kolay", "pratik", "lezzetli", "nefis", "klasik", "orijinal"]
    for kelime in gereksiz_kelimeler:
        aranan_isim = aranan_isim.replace(kelime, "").strip()

    # 2. AŞAMA: İçinde geçiyor mu kontrolü (icontains)
    # Örn: Veritabanında "Etli Kuru Fasulye" varsa ve biz "Kuru Fasulye" arıyorsak yakalar.
    kolay_eslesme = Recipe.objects.filter(title__icontains=aranan_isim).first()
    if kolay_eslesme:
        return kolay_eslesme

    # 3. AŞAMA: Harf hatası veya ufak farklar için Yapay Zeka gibi % Benzerlik Ölçümü
    tum_tarifler = Recipe.objects.all()
    for t in tum_tarifler:
        veritabanindaki_isim = t.title.lower()

        # İki metin birbirine ne kadar benziyor? (0.0 ile 1.0 arası puan verir)
        benzerlik_orani = difflib.SequenceMatcher(None, aranan_isim, veritabanindaki_isim).ratio()

        if benzerlik_orani >= 0.75:  # Eğer %75 ve üzeri benziyorsa "Aynı tarif bu!" de.
            return t

    # Hiçbir teste uymadıysa demek ki gerçekten yepyeni bir tarifmiş
    return None


def gemini_ile_sohbet_et(user, session_id, user_message):
    Chat.objects.create(user=user, session_id=session_id, message=user_message, sender='user')

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    # 🚀 PROMPT GÜNCELLENDİ: Kaç kişilik olduğu eklendi ve parantez yasağı getirildi!
    prompt = f"""
    Senin adın SmartChef. Dünyanın en iyi yapay zeka şefisin.
    Kullanıcı sana yapmak istediği bir yemeğin adını söyleyecek.

    ÇOK ÖNEMLİ KURALLAR:
    1. Cevabını KESİNLİKLE VE SADECE aşağıdaki JSON formatında vermelisin. Başka hiçbir metin ekleme.

    2. MARKET KURALI (ÇOK ÖNEMLİ): Kullanacağın tüm malzemeler standart bir Türk marketinde kolayca bulunabilen şeyler olmalı. Egzotik malzeme KESİNLİKLE KULLANMA.

    3. İSİMLENDİRME KURALI: Malzeme isimleri KISA VE NET olmalı. Asla parantez içi açıklama yapma veya alternatif sunma! (Örn: "Pide (Tırnak veya Lavaş)" YERİNE SADECE "Pide" yaz).

    4. Miktar kısmına SADECE SAYI yaz. Birim kısmına KESİNLİKLE SADECE "gr", "ml" veya "adet" yaz. 

    {{
        "tarif_adi": "İskender Kebap",
        "kac_kisilik": 2,
        "sohbet": "İşte harika bir tarif... (Yapılış aşamaları)",
        "malzemeler": [
            {{"isim": "Dana Kontrfile", "miktar": 350, "birim": "gr"}},
            {{"isim": "Pide", "miktar": 1, "birim": "adet"}},
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