import json
import uuid
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .services import gemini_ile_sohbet_et

@login_required(login_url='giris_yap')
def chat_api_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            kullanici_mesaji = data.get('message')

            if 'chat_session_id' not in request.session:
                request.session['chat_session_id'] = str(uuid.uuid4())
            session_id = request.session['chat_session_id']

            # Arka mutfaktan sözlük (dict) formatında veri geliyor
            yapay_zeka_verisi = gemini_ile_sohbet_et(request.user, session_id, kullanici_mesaji)

            return JsonResponse(yapay_zeka_verisi)
        except Exception as e:
            # Hata anında JavaScript'in çökmesini engellemek için yedek yanıt
            return JsonResponse({"sohbet": "Mutfakta küçük bir kaza oldu, lütfen tekrar dene.", "malzemeler": []})