from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .services import migros_maliyet_hesapla
from recipes.models import Recipe
import json
import traceback
from .models import MarketCost
from recipes.models import Recipe, RecipeIngredient

@login_required(login_url='/hesap/giris/')
def maliyet_hesapla_api(request, recipe_id):
    if request.method == 'POST':
        try:
            recipe = Recipe.objects.get(id=recipe_id)
            data = json.loads(request.body)


            ai_listesi = data.get('malzemeler')


            if ai_listesi is None:
                print("\n[DEDEKTİF] Eski sistemden gelindi! Malzemeler veritabanından çekiliyor...")
                ingredients = RecipeIngredient.objects.filter(recipe=recipe)
                ai_listesi = []
                for m in ingredients:
                    ai_listesi.append({
                        'isim': m.ingredient.name,
                        'miktar': m.quantity,
                        'birim': m.unit
                    })


            if ai_listesi == []:
                 return JsonResponse({
                    'durum': 'basarili',
                    'toplam_sepet': 0,
                    'toplam_tarif_maliyeti': 0,
                    'malzemeler': []
                })


            sonuclar = migros_maliyet_hesapla(ai_listesi)

            if sonuclar.get('durum') == 'basarili':
                MarketCost.objects.create(
                    user=request.user,
                    recipe=recipe,
                    toplam_sepet=sonuclar['toplam_sepet'],
                    porsiyon_maliyeti=sonuclar['toplam_tarif_maliyeti']
                )

            return JsonResponse(sonuclar)

        except Recipe.DoesNotExist:
            return JsonResponse({'durum': 'hata', 'mesaj': 'Tarif bulunamadı'}, status=404)

        except Exception as e:
            print("\n" + "=" * 50)
            print("!!! MİGROS BOTU VEYA API ÇÖKTÜ !!!")
            traceback.print_exc()
            print("=" * 50 + "\n")
            return JsonResponse({'durum': 'hata', 'mesaj': str(e)}, status=500)

    return JsonResponse({'durum': 'hata', 'mesaj': 'Bu adrese sadece POST isteği atılabilir.'}, status=405)