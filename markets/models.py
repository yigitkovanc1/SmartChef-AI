import uuid
from django.db import models
from recipes.models import Ingredient # Mimari bağlantı noktası!

class Market(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    base_url = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

class MarketProduct(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='products')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='market_products')
    product_name = models.CharField(max_length=255)
    product_url = models.TextField(blank=True, null=True)
    base_quantity = models.DecimalField(max_digits=8, decimal_places=2)
    base_unit = models.CharField(max_length=50)

    def __str__(self):
        return self.product_name

class PriceHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    market_product = models.ForeignKey(MarketProduct, on_delete=models.CASCADE, related_name='price_history')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    recorded_at = models.DateTimeField(auto_now_add=True)
