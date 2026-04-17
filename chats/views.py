from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json
import uuid
from django.http import JsonResponse
from .services import gemini_ile_sohbet_et, benzer_tarif_bul  # YENİ: Arama motorunu dahil ettik
import traceback
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
            # 1. AKILLI HAFIZA KONTROLÜ (Services.py'daki zekayı kullanıyoruz)
            # ==========================================
            mevcut_tarif = benzer_tarif_bul(kullanici_mesaji)

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
            # 2. YAPAY ZEKAYA SOR (Hata Buradaydı, Geri Getirdik!)
            # ==========================================
            yapay_zeka_verisi = gemini_ile_sohbet_et(request.user, session_id, kullanici_mesaji)
            return JsonResponse(yapay_zeka_verisi)

        except Exception as e:
            print("\n" + "=" * 50)
            print("!!! YAPAY ZEKA VEYA KAYIT SİSTEMİ ÇÖKTÜ !!!")
            traceback.print_exc()
            print("=" * 50 + "\n")
            return JsonResponse({"sohbet": "Mutfakta küçük bir kaza oldu, lütfen tekrar dene.", "malzemeler": []})

    # Eğer GET isteği atılırsa güvenlik kalkanı
    return JsonResponse({"sohbet": "Bu adrese sadece POST isteği atılabilir.", "malzemeler": []}, status=405)