import uuid
from django.db import models
from django.contrib.auth.models import User

class Ingredient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Recipe(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    instructions = models.TextField()
    prep_time_minutes = models.IntegerField(blank=True, null=True)
    cook_time_minutes = models.IntegerField(blank=True, null=True)
    servings = models.IntegerField(blank=True, null=True)
    difficulty_level = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='tarif_fotograflari/', null=True, blank=True)

    def __str__(self):
        return self.title

class RecipeIngredient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.recipe.title} -> {self.ingredient.name} ({self.quantity} {self.unit})"

from django.contrib.auth.models import User # Eğer en üstte yoksa bunu da ekle

# ==========================================
# FAVORİ TARİFLER TABLOSU
# ==========================================
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Bir kullanıcı aynı tarifi 2 kez favoriye ekleyemesin diye kilit koyuyoruz.
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f"{self.user.username} - {self.recipe.title}"
class RecipeCostHistory(models.Model):
        recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='cost_history')
        total_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Toplam Maliyet (TL)")
        date_recorded = models.DateField(auto_now_add=True, verbose_name="Kayıt Tarihi")

        class Meta:
            ordering = ['-date_recorded']  # En yeni tarih en üstte çıksın

        def __str__(self):
            return f"{self.recipe.title} - {self.total_cost} ₺ ({self.date_recorded})"