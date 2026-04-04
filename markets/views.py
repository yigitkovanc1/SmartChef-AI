from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .services import migros_maliyet_hesapla
from recipes.models import Recipe, RecipeIngredient
import json
import traceback  # BÜYÜK DEDEKTİF KÜTÜPHANESİ
from .models import MarketCost

@login_required(login_url='/hesap/giris/')  # Eğer oturum düşerse hata patlatmasın diye ekledik
def maliyet_hesapla_api(request, recipe_id):
    try:
        # 1. Tarifi ve malzemelerini veritabanından çek
        recipe = Recipe.objects.get(id=recipe_id)
        ingredients = RecipeIngredient.objects.filter(recipe=recipe)

        # 2. Malzemeleri botun anladığı formata (liste) çevir
        ai_listesi = []
        for m in ingredients:
            ai_listesi.append({
                'isim': m.ingredient.name,
                'miktar': m.quantity,
                'birim': m.unit
            })

        print(f"\n[DEDEKTİF] Bot için hazırlanan liste: {ai_listesi}")

        # 3. MİGROS BOTUNU ATEŞLE! 🚀
        sonuclar = migros_maliyet_hesapla(ai_listesi)
        if sonuclar.get('durum') == 'basarili':
            MarketCost.objects.create(
                user=request.user,
                recipe=recipe,
                toplam_sepet=sonuclar['toplam_sepet'],
                porsiyon_maliyeti=sonuclar['toplam_tarif_maliyeti']
            )
        print(f"[DEDEKTİF] Bottan dönen sonuç: {sonuclar}")

        return JsonResponse(sonuclar)

    except Recipe.DoesNotExist:
        return JsonResponse({'durum': 'hata', 'mesaj': 'Tarif bulunamadı'}, status=404)

    except Exception as e:
        # 4. GİZLİ HATALARI YAKALAYAN ZIRH
        print("\n" + "=" * 50)
        print("!!! MİGROS BOTU VEYA API ÇÖKTÜ !!!")
        traceback.print_exc()  # PyCharm terminaline kırmızı hatayı basar
        print("=" * 50 + "\n")

        # Javascript'in saçmalamaması için hatayı json olarak dönüyoruz
        return JsonResponse({'durum': 'hata', 'mesaj': str(e)}, status=500)