from django.urls import path
from . import views

urlpatterns = [
    # 1. Kullanıcı siteadi.com/chat/ adresine girdiğinde tasarımı (chat.html) görür
    path('', views.chat_sayfasi_view, name='chat_sayfasi'),

    # 2. Javascript arka planda mesaj atarken burayı (senin API'ni) kullanır
    path('api/', views.chat_api_view, name='chat_api'),
]