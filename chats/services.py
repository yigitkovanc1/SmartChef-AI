import os
import json
import time
from datetime import datetime
from google import genai
from .models import Chat
from recipes.models import Recipe, Ingredient, RecipeIngredient
import difflib
import re


def benzer_tarif_bul(aranan_isim):
    if not aranan_isim:
        return None

    aranan_isim = aranan_isim.lower().strip()
    silinecekler = r'\b(bana|bir|tarifi|tarif|tarifleri|yemeği|ev yapımı|kolay|pratik|lezzetli|nefis|klasik|orijinal|özel|usulü|nasıl|yapılır|istiyorum|ver)\b'
    temiz_isim = re.sub(silinecekler, '', aranan_isim).strip()
    temiz_isim = " ".join(temiz_isim.split())

    if not temiz_isim:
        return None

    tum_tarifler = Recipe.objects.all()

    for t in tum_tarifler:
        db_isim = t.title.lower().replace('*', '').strip()
        if db_isim == temiz_isim:
            return t

    for t in tum_tarifler:
        db_isim = t.title.lower().replace('*', '').strip()
        if db_isim.startswith(temiz_isim) or temiz_isim.startswith(db_isim):
            return t

        benzerlik_orani = difflib.SequenceMatcher(None, temiz_isim, db_isim).ratio()
        if benzerlik_orani >= 0.80:
            return t

    return None


def gemini_ile_sohbet_et(user, session_id, user_message):
    Chat.objects.create(user=user, session_id=session_id, message=user_message, sender='user')

    # ==========================================
    # TASARRUF MODU: API'YE GİTMEDEN ÖNCE VERİTABANINA BAK
    # ==========================================
    mevcut_tarif = benzer_tarif_bul(user_message)

    if mevcut_tarif:
        sohbet_metni = mevcut_tarif.instructions
        malzemeler_db = RecipeIngredient.objects.filter(recipe=mevcut_tarif)

        malzemeler_liste = []
        for m in malzemeler_db:
            malzemeler_liste.append({
                "isim": m.ingredient.name.title(),
                "miktar": float(m.quantity),
                "birim": m.unit,
                "evde_var": False
            })

        Chat.objects.create(user=user, session_id=session_id, message=sohbet_metni, sender='ai')

        # Ajan Kodu (Terminalden kontrol etmek istersen)
        print("\n" + "=" * 40)
        print("🕵️‍♂️ DEDEKTİF RAPORU (ZIRHDAN ÇIKAN VERİ):")
        for ajan_malz in malzemeler_liste:
            print(f"İsim: '{ajan_malz['isim']}' | Miktar: {ajan_malz['miktar']}")
        print("=" * 40 + "\n")

        return {
            "sohbet": sohbet_metni,
            "malzemeler": malzemeler_liste,
            "recipe_id": str(mevcut_tarif.id)
        }
    # ==========================================

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    prompt = f"""
    Senin adın SmartChef. Dünyanın en iyi yapay zeka şefisin.
    Kullanıcı sana YA yapmak istediği yemeğin adını söyleyecek YA DA "Elimde şunlar var: domates, tavuk..." diyerek elindeki malzemeleri verip bir tarif uydurmanı isteyecek.

    ÇOK ÖNEMLİ KURALLAR:
    1. EĞER KULLANICI MALZEME VERİRSE (Sihirli Dolap): Verdiği malzemeleri BAŞROLDE kullan. Sadece yemeği bağlamak için çok temel eksikleri (yağ, tuz, un vb.) listeye ekle.
    2. FORMAT KURALI: Cevabını KESİNLİKLE VE SADECE aşağıdaki JSON formatında vermelisin. Başka hiçbir metin ekleme.
    3. MARKET KURALI: Egzotik malzeme KULLANMA. 'Sıvı Yağ' yerine 'Ayçiçek Yağı' yaz. 'Kıyma' yerine 'Dana Kıyma' yaz.
    4. İSİMLENDİRME KURALI: Miktarları toplayıp tek kalem yaz.
    5. "EVDE VAR" ZEKASI (ÇOK ÖNEMLİ!): Kullanıcının mesajında sana verdiği (yani evinde olan) malzemeler için "evde_var" değerini true yap. Senin yemeği tamamlamak için mecburen eklediğin ekstra malzemeler için false yap! (Kullanıcı hiç malzeme vermeden direkt "Makarna yap" derse hepsini false yap).

    {{
        "tarif_adi": "Fırında Kaşarlı Tavuk",
        "kac_kisilik": 2,
        "sohbet": "İşte elindeki malzemelerle harika bir tarif! 1. Adım... 2. Adım... (YAPILIŞ AŞAMALARINI KESİNLİKLE EKSİKSİZ, UZUN UZUN VE DETAYLI YAZ)",
        "malzemeler": [
            {{"isim": "Banvit Piliç Göğüs", "miktar": 400, "birim": "gr", "evde_var": true}},
            {{"isim": "Kaşar Peyniri", "miktar": 100, "birim": "gr", "evde_var": true}},
            {{"isim": "Ayçiçek Yağı", "miktar": 30, "birim": "ml", "evde_var": false}}
        ]
    }}

    Kullanıcının isteği: {user_message}
    """

    yeni_tarif_id = None

    try:
        for deneme in range(5):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                break
            except Exception as api_hata:
                if "503" in str(api_hata) and deneme < 4:
                    bekleme_suresi = (deneme + 1) * 3
                    print(
                        f"⏳ Google fena tıkalı. {bekleme_suresi} saniye nefes alıp tekrar saldırıyoruz... (Deneme {deneme + 1}/5)")
                    time.sleep(bekleme_suresi)
                else:
                    raise api_hata

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

        orijinal_tarif_adi = ai_data.get("tarif_adi", "İsimsiz Tarif")
        kac_kisilik = ai_data.get("kac_kisilik", 1)
        sohbet_metni = ai_data.get("sohbet", "İşte harika bir tarif şef!")
        malzemeler_listesi = ai_data.get("malzemeler", [])

        sohbet_metni = f"🍽️ **Bu tarif {kac_kisilik} kişiliktir.**\n\n" + sohbet_metni

        if malzemeler_listesi:

            # =========================================================
            # 1. ADIM: YAPAY ZEKANIN HALÜSİNASYONLARINI TEMİZLE
            # =========================================================
            for malz in malzemeler_listesi:
                if "isim" not in malz:
                    malz["isim"] = malz.get("ad", malz.get("malzeme_adi",
                                                           malz.get("malzeme", malz.get("urun", "Bilinmeyen Malzeme"))))

                ham_miktar = malz.get("miktar", malz.get("adet", malz.get("gram", malz.get("olcu", 0))))
                try:
                    if isinstance(ham_miktar, str):
                        ham_miktar = ham_miktar.replace(',', '.')
                    malz["miktar"] = float(ham_miktar)
                except (ValueError, TypeError):
                    malz["miktar"] = 0.0

                if "birim" not in malz:
                    malz["birim"] = malz.get("olcu_birimi", malz.get("cins", ""))

                if "evde_var" not in malz:
                    malz["evde_var"] = False
                elif isinstance(malz["evde_var"], str):
                    malz["evde_var"] = malz["evde_var"].lower() in ["true", "var", "evet", "1"]

            # =========================================================
            # 2. ADIM: SİHİRLİ DOLAP VIP ZIRHI VE KAYIT
            # =========================================================
            sihirli_dolap_kullanildi_mi = any(m.get("evde_var") is True for m in malzemeler_listesi)

            if sihirli_dolap_kullanildi_mi:
                # Kullanıcı malzeme verdiyse bu %100 YENİ bir tariftir.
                isim = user.first_name if user.first_name else user.username
                isim = isim.capitalize()
                tarih_str = datetime.now().strftime("%d.%m.%y")
                kaydedilecek_isim = f"{tarih_str} Tarihli {isim}'in {orijinal_tarif_adi}"

                # İŞTE BÜYÜ BURADA: Eski tarifi aramayı tamamen İPTAL ediyoruz!
                mevcut_tarif = None
            else:
                kaydedilecek_isim = orijinal_tarif_adi
                mevcut_tarif = benzer_tarif_bul(orijinal_tarif_adi)

            # EĞER YENİ BİR TARİFSE VERİTABANINA DİZ!
            if not mevcut_tarif:
                yeni_tarif = Recipe.objects.create(
                    user=user,
                    title=kaydedilecek_isim,
                    instructions=sohbet_metni,
                    servings=kac_kisilik
                )
                yeni_tarif_id = str(yeni_tarif.id)

                for malz in malzemeler_listesi:
                    malz_isim = str(malz.get("isim", "")).lower().strip()
                    miktar = float(malz.get("miktar", 0.0))
                    birim = str(malz.get("birim", "")).strip()

                    # Malzeme boş veya bilinmeyen değilse kaydet
                    if malz_isim and malz_isim != "bilinmeyen malzeme":
                        ingredient_obj, created = Ingredient.objects.get_or_create(name=malz_isim)
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
        traceback.print_exc()

    db_kayit = sohbet_metni
    if malzemeler_listesi:
        db_kayit += "\n\nMalzemeler:\n- " + "\n- ".join(
            [f"{m.get('miktar')} {m.get('birim')} {m.get('isim')}" for m in malzemeler_listesi])

    Chat.objects.create(user=user, session_id=session_id, message=db_kayit, sender='ai')

    return {
        "sohbet": sohbet_metni,
        "malzemeler": malzemeler_listesi,
        "recipe_id": yeni_tarif_id
    }