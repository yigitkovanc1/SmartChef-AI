from django.urls import path
from . import views

urlpatterns = [
    path('soru-sor/', views.chat_api_view, name='chat_api'),
]