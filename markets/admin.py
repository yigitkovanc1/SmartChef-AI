from django.contrib import admin
from .models import Market, MarketProduct, PriceHistory

admin.site.register(Market)
admin.site.register(MarketProduct)
admin.site.register(PriceHistory)
