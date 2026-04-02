from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Recipe, Favorite


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

    # Sayfayı yenilemeden (AJAX ile) cevap dönmek için JSON kullanıyoruz
    return JsonResponse({'status': 'ok', 'is_favorite': is_favorite})
# YENİ: Anasayfa Vitrini
def anasayfa_view(request):
    # Veritabanından rastgele (?) 3 tarif çekiyoruz
    onerilen_tarifler = Recipe.objects.all().order_by('?')[:3]
    return render(request, 'home.html', {'onerilen_tarifler': onerilen_tarifler})