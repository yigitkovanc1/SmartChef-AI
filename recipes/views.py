from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Recipe, RecipeIngredient, Favorite

@login_required
def favori_toggle_view(request, recipe_id):
    # Tarifi bul, yoksa 404 hatası ver
    recipe = get_object_or_404(Recipe, id=recipe_id)

    # Bu kullanıcı bu tarifi daha önce favoriye eklemiş mi?
    favori_var_mi = Favorite.objects.filter(user=request.user, recipe=recipe)

    if favori_var_mi.exists():
        favori_var_mi.delete()  # Varsa sil (Favoriden çıkar)
        is_favorite = False
    else:
        Favorite.objects.create(user=request.user, recipe=recipe)  # Yoksa ekle
        is_favorite = True

    # DÜZELTME: JavaScript kodu animasyonu başlatmak için 'success' kelimesini bekliyor.
    # O yüzden 'ok' yerine 'success' döndürüyoruz!
    return JsonResponse({'status': 'success', 'is_favorite': is_favorite})


def anasayfa_view(request):

    onerilen_tarifler = Recipe.objects.exclude(title__icontains='Tarihli').order_by('?')[:3]
    return render(request, 'home.html', {'onerilen_tarifler': onerilen_tarifler})


@login_required(login_url='/hesap/giris/')
def tarif_detay_view(request, recipe_id):

    tarif = get_object_or_404(Recipe, id=recipe_id)


    malzemeler = RecipeIngredient.objects.filter(recipe=tarif)


    is_favorite = Favorite.objects.filter(user=request.user, recipe=tarif).exists()

    context = {
        'tarif': tarif,
        'malzemeler': malzemeler,
        'is_favorite': is_favorite
    }

    return render(request, 'tarif_detay.html', context)


@login_required(login_url='/hesap/giris/')
def tarif_defterim_view(request):
    # 1. Kullanıcının yapay zekaya ürettirdiği kendi tarifleri
    kullanici_tarifleri = Recipe.objects.filter(user=request.user).order_by('-id')


    favori_kayitlari = Favorite.objects.filter(user=request.user).select_related('recipe').order_by('-id')
    favori_tarifler = [kayit.recipe for kayit in favori_kayitlari]

    context = {
        'kullanici_tarifleri': kullanici_tarifleri,
        'favori_tarifler': favori_tarifler,
    }

    return render(request, 'tarif_defterim.html', context)