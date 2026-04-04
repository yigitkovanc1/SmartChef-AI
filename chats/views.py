from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json
import uuid
from django.http import JsonResponse
from .services import gemini_ile_sohbet_et
import traceback
from recipes.models import Recipe, Ingredient, RecipeIngredient

# YENİ: Veritabanındaki tarif ve malzemeleri çekmek için modelleri dahil ediyoruz
from recipes.models import Recipe, RecipeIngredient

@login_required(login_url='giris_yap')
def chat_sayfasi_view(request):
    return render(request, 'chat.html')


@login_required(login_url='giris_yap')
def chat_api_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            kullanici_mesaji = data.get('message', '')

            if 'chat_session_id' not in request.session:
                request.session['chat_session_id'] = str(uuid.uuid4())
            session_id = request.session['chat_session_id']

            # ==========================================
            # 🚀 BÜYÜK OPTİMİZASYON: VERİTABANI KONTROLÜ
            # ==========================================
            mesaj_kucuk = kullanici_mesaji.lower()
            mevcut_tarif = None

            for tarif in Recipe.objects.all():
                if tarif.title.lower() in mesaj_kucuk:
                    mevcut_tarif = tarif
                    break

            if mevcut_tarif:
                malzemeler_query = RecipeIngredient.objects.filter(recipe=mevcut_tarif)
                malzemeler_listesi = [
                    f"{m.quantity} {m.unit} {m.ingredient.name.title()}" for m in malzemeler_query
                ]
                return JsonResponse({
                    "sohbet": f"⚡ *(Hafızadan hızlıca getirildi)*\n\nİşte efsane **{mevcut_tarif.title}** tarifi:\n\n{mevcut_tarif.instructions}",
                    "malzemeler": malzemeler_listesi,
                    "recipe_id": str(mevcut_tarif.id)
                })

            # ==========================================
            # EĞER TARİF YOKSA: YAPAY ZEKAYA (GEMINI) SOR
            # ==========================================
            yapay_zeka_verisi = gemini_ile_sohbet_et(request.user, session_id, kullanici_mesaji)

            # 🚀 İŞTE SİHİRLİ DOKUNUŞ BURADA BAŞLIYOR 🚀
            # Eğer yapay zeka bize bir malzeme listesi döndüyse (yani bu bir tarifse):
            if yapay_zeka_verisi.get('malzemeler') and len(yapay_zeka_verisi['malzemeler']) > 0:

                # 1. Gemini'nin ürettiği tarifi KALICI olarak veritabanına kaydet
                yeni_tarif = Recipe.objects.create(
                    user=request.user,  # 🚀 İŞTE EKSİK OLAN HAYATİ SATIR BU!
                    title=kullanici_mesaji.capitalize(),
                    instructions=yapay_zeka_verisi.get('sohbet', 'Yapay zeka tarifi...')
                )

                # 2. Malzemeleri de veritabanına (RecipeIngredient) kaydet
                for malzeme_metni in yapay_zeka_verisi['malzemeler']:
                    # Malzemeyi veritabanında bul veya yarat
                    ing_obj, created = Ingredient.objects.get_or_create(name=malzeme_metni)

                    # Tarife bağla
                    RecipeIngredient.objects.create(
                        recipe=yeni_tarif,
                        ingredient=ing_obj,
                        quantity=1,  # Varsayılan
                        unit=""  # Varsayılan
                    )

                # 3. VERİTABANI ID'SİNİ JAVASCRIPT'E GÖNDER! (Artık 404 hatası yok)
                yapay_zeka_verisi['recipe_id'] = str(yeni_tarif.id)

            return JsonResponse(yapay_zeka_verisi)

        except Exception as e:
            # DEDEKTİF BURADA DEVREYE GİRİYOR
            print("\n" + "=" * 50)
            print("!!! YAPAY ZEKA VEYA KAYIT SİSTEMİ ÇÖKTÜ !!!")
            traceback.print_exc()  # PyCharm terminaline kırmızı hatayı basar
            print("=" * 50 + "\n")

            return JsonResponse({"sohbet": "Mutfakta küçük bir kaza oldu, lütfen tekrar dene.", "malzemeler": []})