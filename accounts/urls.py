from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('kayit/', views.kayit_ol_view, name='kayit_ol'),
    path('giris/', views.giris_yap_view, name='giris_yap'),
    path('cikis/', views.cikis_yap_view, name='cikis_yap'),
    path('anasayfa/', views.ana_sayfa_view, name='ana_sayfa'),
    path('sifremi-unuttum/', views.sifremi_unuttum_view, name='sifremi_unuttum'),
    path('sifre-sifirla/', views.sifre_sifirla_view, name='sifre_sifirla'),
    path('profil/', views.profil_view, name='profil_sayfasi'),
    path('cikis/', auth_views.LogoutView.as_view(next_page='home'), name='cikis_yap'),
    path('dashboard/', views.dashboard_view, name='dashboard_sayfasi'),
    path('sifre-degistir/', views.sifre_degistir_view, name='sifre_degistir'),
    path('bio-guncelle/', views.bio_guncelle_view, name='bio_guncelle'),
]

