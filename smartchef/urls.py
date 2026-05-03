from django.contrib import admin
from django.urls import path, include
from recipes.views import anasayfa_view  # YENİ: Kendi yazdığımız fonksiyonu çağırdık
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Anasayfa view'ini nereden çekiyorsan o import'un yukarıda olduğundan emin ol!
# Örnek: from recipes.views import anasayfa_view

urlpatterns = [
    path('admin/', admin.site.urls),

    # YENİ: Artık anasayfa için kendi yazdığımız anasayfa_view çalışacak
    path('', anasayfa_view, name='home'),

    # UYGULAMA ROTALARI (Tertemiz ve tek sefer)
    path('chat/', include('chats.urls')),
    path('hesap/', include('accounts.urls')),
    path('tarifler/', include('recipes.urls')), # Bütün tarif işlemleri buradan geçecek!
    path('market/', include('markets.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)