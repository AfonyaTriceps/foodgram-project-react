from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    IngredientViewSet,
    RecipeFavoriteView,
    RecipeViewSet,
    ShoppingCartListView,
    ShoppingCartView,
    TagViewSet,
)

app_name = 'api'

router = DefaultRouter()

router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path(
        'recipes/<int:pk>/favorite/',
        RecipeFavoriteView.as_view(),
        name='favorite',
    ),
    path(
        'recipes/<int:pk>/shopping_cart/',
        ShoppingCartView.as_view(),
        name='shopping_cart',
    ),
    path(
        'recipes/download_shopping_cart/',
        ShoppingCartListView.as_view(),
        name='shopping_cart',
    ),
    path('', include(router.urls)),
]
