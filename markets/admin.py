from django.contrib import admin
from .models import Market, MarketProduct, PriceHistory

admin.site.register(Market)
admin.site.register(MarketProduct)
admin.site.register(PriceHistory)

from django.contrib import admin
from .models import MarketCost  # Modelinin adı MarketCost ise bunu kullan, farklıysa değiştir


@admin.register(MarketCost)
class MarketCostAdmin(admin.ModelAdmin):
    # Admin panelinde yan yana hangi sütunlar görünsün?
    list_display = ('recipe', 'user', 'porsiyon_maliyeti', 'toplam_sepet', 'tarih')

    # Sağ tarafa filtreleme menüsü ekleyelim (Tarihe veya kullanıcıya göre filtrele)
    list_filter = ('user', 'tarih')

    # Arama çubuğu ekleyelim (Tarif adına veya kullanıcı adına göre ara)
    search_fields = ('recipe__title', 'user__username')
