from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .services import migros_maliyet_hesapla
from recipes.models import Recipe
import json
import traceback
from .models import MarketCost


@login_required(login_url='/hesap/giris/')
def maliyet_hesapla_api(request, recipe_id):
    # EĞER İSTEK POST İLE GELDİYSE (Yani bizim yeni zeki Javascript'imizden geldiyse)
    if request.method == 'POST':
        try:
            recipe = Recipe.objects.get(id=recipe_id)

            # 1. Zarfı (Paketi) Aç! Front-end'den gelen JSON verisini okuyoruz.
            data = json.loads(request.body)
            ai_listesi = data.get('malzemeler', [])

            print(f"\n[DEDEKTİF] Kullanıcının seçtiği EKSİK ve ÇARPILMIŞ malzeme listesi: {ai_listesi}")

            # 2. MİGROS BOTUNU ATEŞLE (Direkt kullanıcının gönderdiği listeyle!)
            sonuclar = migros_maliyet_hesapla(ai_listesi)

            # 3. Sonuç başarılıysa Veritabanına "Muhasebe Kaydı" at
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
            print("\n" + "=" * 50)
            print("!!! MİGROS BOTU VEYA API ÇÖKTÜ !!!")
            traceback.print_exc()
            print("=" * 50 + "\n")
            return JsonResponse({'durum': 'hata', 'mesaj': str(e)}, status=500)

    # Eğer birisi tarayıcıdan direkt linke girmeye çalışırsa (GET) reddet
    return JsonResponse({'durum': 'hata', 'mesaj': 'Bu adrese sadece POST isteği atılabilir.'}, status=405)