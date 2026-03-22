from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hesap/', include('accounts.urls')),
    path('yapay-zeka/', include('chats.urls')), # YENİ EKLENEN YAPAY ZEKA YOLU
]