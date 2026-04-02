from django.contrib import admin
from django.urls import path, include
from recipes.views import anasayfa_view  # YENİ: Kendi yazdığımız fonksiyonu çağırdık

urlpatterns = [
    path('admin/', admin.site.urls),

    # YENİ: Artık anasayfa için kendi yazdığımız anasayfa_view çalışacak
    path('', anasayfa_view, name='home'),

    path('chat/', include('chats.urls')),
    path('hesap/', include('accounts.urls')),
    path('tarifler/', include('recipes.urls')),
]