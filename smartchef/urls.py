from django.contrib import admin
from django.urls import path, include
from recipes.views import anasayfa_view  # YENİ: Kendi yazdığımız fonksiyonu çağırdık
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # YENİ: Artık anasayfa için kendi yazdığımız anasayfa_view çalışacak
    path('', anasayfa_view, name='home'),

    path('chat/', include('chats.urls')),
    path('hesap/', include('accounts.urls')),
    path('tarifler/', include('recipes.urls')),

    path('admin/', admin.site.urls),
    path('', include('recipes.urls')), # Veya senin anasayfa yönlendirmen
    # ... senin diğer yolların ...
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)