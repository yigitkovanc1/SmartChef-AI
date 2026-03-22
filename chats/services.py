import os
import json
from google import genai
from .models import Chat
from recipes.models import Recipe, Ingredient, RecipeIngredient


def gemini_ile_sohbet_et(user, session_id, user_message):
    Chat.objects.create(user=user, session_id=session_id, message=user_message, sender='user')

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    # JÜRİ ŞOVU: Yapay zekadan malzemeleri gram/ml olarak JSON formatında istiyoruz.
    prompt = f"""
    Senin adın SmartChef. Dünyanın en iyi yapay zeka şefisin.
    Kullanıcı sana yapmak istediği bir yemeğin adını söyleyecek.

    ÇOK ÖNEMLİ KURAL: Cevabını KESİNLİKLE VE SADECE aşağıdaki JSON formatında vermelisin. Başka hiçbir metin ekleme.

    Miktar kısmına SADECE SAYI yaz. 
    Birim kısmına KESİNLİKLE SADECE "gr", "ml" veya "adet" yaz. 
    Eğer tarifte "yemek kaşığı", "su bardağı", "tutam" gibi ölçüler varsa, porsiyona göre bunları tahmini gram veya mililitreye çevir (Örn: 1 yemek kaşığı = ortalama 15 gr, 1 su bardağı = ortalama 200 ml).

    {{
        "tarif_adi": "Hamburger",
        "sohbet": "İşte harika bir tarif... (Yapılış aşamaları)",
        "malzemeler": [
            {{"isim": "Dana Kıyma", "miktar": 200, "birim": "gr"}},
            {{"isim": "Sıvı Yağ", "miktar": 15, "birim": "ml"}},
            {{"isim": "Cheddar Peyniri", "miktar": 1, "birim": "adet"}}
        ]
    }}

    Kullanıcının isteği: {user_message}
    """

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

        ai_data = json.loads(raw_text)

        tarif_adi = ai_data.get("tarif_adi", "İsimsiz Tarif")
        sohbet_metni = ai_data.get("sohbet", "İşte harika bir tarif şef!")
        malzemeler_listesi = ai_data.get("malzemeler", [])

        # --- ARKA MUTFAK İŞLEMLERİ: VERİTABANINA KAYIT ---
        if malzemeler_listesi:
            # JÜRİ ŞOVU 2: Kopyalanmayı önleyen kontrol (Sistemde bu tarif var mı?)
            mevcut_tarif = Recipe.objects.filter(title__iexact=tarif_adi).first()

            if not mevcut_tarif:  # Sadece sistemde YOKSA kaydet
                # 1. Tarifi Veritabanına Oluştur
                yeni_tarif = Recipe.objects.create(
                    user=user,
                    title=tarif_adi,
                    instructions=sohbet_metni
                )

                # 2. Malzemeleri Tek Tek Dön ve Veritabanına Ekle
                for malz in malzemeler_listesi:
                    isim = malz.get("isim", "").lower().strip()
                    miktar = malz.get("miktar", 0)
                    birim = malz.get("birim", "")

                    if isim:
                        # a. Malzeme yoksa yarat, varsa olanı al
                        ingredient_obj, created = Ingredient.objects.get_or_create(name=isim)

                        # b. Tarifi ve Malzemeyi birbirine bağla
                        RecipeIngredient.objects.create(
                            recipe=yeni_tarif,
                            ingredient=ingredient_obj,
                            quantity=miktar,
                            unit=birim
                        )
        # --------------------------------------------------

    except Exception as e:
        sohbet_metni = "Üzgünüm şef, tarif defterimi bulamıyorum. Lütfen yemeğin adını tekrar yazar mısın?"
        malzemeler_listesi = []
        # Eğer arka planda bir şey patlarsa, terminale kırmızıyla yazsın diye bunu ekledim:
        print(f"\n--- ARKA MUTFAKTA BİR ŞEY PATLADI ---\nHATA: {e}\n-----------------------------------\n")

    # Chat ekranında göstermek için metni birleştiriyoruz
    db_kayit = sohbet_metni
    if malzemeler_listesi:
        db_kayit += "\n\nMalzemeler:\n- " + "\n- ".join(
            [f"{m.get('miktar')} {m.get('birim')} {m.get('isim')}" for m in malzemeler_listesi])

    Chat.objects.create(user=user, session_id=session_id, message=db_kayit, sender='ai')

    # Ön yüze veriyi gönder
    return {"sohbet": sohbet_metni,
            "malzemeler": [f"{m.get('miktar')} {m.get('birim')} {m.get('isim')}" for m in malzemeler_listesi]}