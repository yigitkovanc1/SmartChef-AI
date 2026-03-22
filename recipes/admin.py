from django.contrib import admin
from .models import Ingredient, Recipe, RecipeIngredient

# JÜRİ ŞOVU: Admin panelinde tabloları excel gibi sütun sütun göster
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at')
    search_fields = ('title',)

class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'quantity', 'unit') # O çirkin yazı yerine bu sütunlar gelecek!
    list_filter = ('recipe',) # Sağ tarafa "Tarife Göre Filtrele" menüsü ekler

admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)