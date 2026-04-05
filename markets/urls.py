from django.urls import path
from .views import maliyet_hesapla_api
from . import views

urlpatterns = [
    path('hesapla/<str:recipe_id>/', maliyet_hesapla_api, name='maliyet_hesapla'),
    path('hesapla/api/<uuid:recipe_id>/', views.maliyet_hesapla_api, name='migros_api'),
]