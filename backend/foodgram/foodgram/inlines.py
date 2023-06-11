from django.contrib import admin

from recipes.models import RecipeIngredients


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredients
    extra = 1
    min_num = 1
