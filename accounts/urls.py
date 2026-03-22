from django.urls import path
from . import views

urlpatterns = [
    path('kayit/', views.kayit_ol_view, name='kayit_ol'),
    path('giris/', views.giris_yap_view, name='giris_yap'),
    path('cikis/', views.cikis_yap_view, name='cikis_yap'),
    path('anasayfa/', views.ana_sayfa_view, name='ana_sayfa'),
    path('sifremi-unuttum/', views.sifremi_unuttum_view, name='sifremi_unuttum'),
    path('sifre-sifirla/', views.sifre_sifirla_view, name='sifre_sifirla'),
]

