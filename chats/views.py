from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json
import uuid
from django.http import JsonResponse
from .services import gemini_ile_sohbet_et
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

            # Veritabanımızdaki tüm tariflerin isimlerini kontrol et
            for tarif in Recipe.objects.all():
                if tarif.title.lower() in mesaj_kucuk:
                    mevcut_tarif = tarif
                    break # Bulduğumuz an döngüyü durdur

            # Eğer tarif veritabanında VARSA! (Yapay zekaya hiç bulaşma)
            if mevcut_tarif:
                malzemeler_query = RecipeIngredient.objects.filter(recipe=mevcut_tarif)
                malzemeler_listesi = [
                    f"{m.quantity} {m.unit} {m.ingredient.name.title()}" for m in malzemeler_query
                ]

                # Sistemi hiç yormadan Json dön
                return JsonResponse({
                    "sohbet": f"⚡ *(Hafızadan hızlıca getirildi)*\n\nİşte efsane **{mevcut_tarif.title}** tarifi:\n\n{mevcut_tarif.instructions}",
                    "malzemeler": malzemeler_listesi,
                    "recipe_id": str(mevcut_tarif.id)  # YENİ: Butonun çalışması için ID'yi gönderiyoruz
                })
            # ==========================================
            # EĞER TARİF YOKSA: YAPAY ZEKAYA (GEMINI) SOR
            # ==========================================
            yapay_zeka_verisi = gemini_ile_sohbet_et(request.user, session_id, kullanici_mesaji)

            return JsonResponse(yapay_zeka_verisi)

        except Exception as e:
            return JsonResponse({"sohbet": "Mutfakta küçük bir kaza oldu, lütfen tekrar dene.", "malzemeler": []})