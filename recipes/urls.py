from django.urls import path
from . import views


urlpatterns = [
    # Az önce yazdığımız Favori Ekle/Çıkar rotası (UUID veya int kullanmana göre ID kısmını ayarladık)
    path('favori-yap/<uuid:recipe_id>/', views.favori_toggle_view, name='favori_toggle'),

    # İleride tarif detay sayfası vs. eklersen buraya alt alta yazacağız
    path('tarif/<uuid:recipe_id>/', views.tarif_detay_view, name='tarif_detay'),
]