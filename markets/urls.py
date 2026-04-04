from django.urls import path
from .views import maliyet_hesapla_api

urlpatterns = [
    path('hesapla/<str:recipe_id>/', maliyet_hesapla_api, name='maliyet_hesapla'),
]