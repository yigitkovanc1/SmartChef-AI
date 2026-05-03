


from django.urls import path
from . import views

urlpatterns = [
    # DÜZELTME BURADA: 'favori-yap' tabelasını JavaScript'in aradığı 'toggle-favorite' ile değiştirdik!
    path('toggle-favorite/<uuid:recipe_id>/', views.favori_toggle_view, name='favori_toggle'),

    # İleride tarif detay sayfası vs. eklersen buraya alt alta yazacağız
    path('tarif/<uuid:recipe_id>/', views.tarif_detay_view, name='tarif_detay'),

    path('defterim/', views.tarif_defterim_view, name='tarif_defterim'),
]