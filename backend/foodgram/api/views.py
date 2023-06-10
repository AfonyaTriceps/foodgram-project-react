from collections import defaultdict

from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets

from api.filters import IngredientFilter, RecipeFilter
from api.mixins import BaseRetrieveDestroyViewSetView, ListViewSet, RetrieveListViewSet
from api.pagination import CustomPageNumberPagination
from api.permissions import IsAdminOwnerOrReadOnly
from api.serializers import (
    IngredientSerializer,
    MiniRecipeSerializer,
    RecipeSerializer,
    RecipeWriteSerializer,
    TagSerializer,
)
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


class TagViewSet(RetrieveListViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientViewSet(RetrieveListViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAdminOwnerOrReadOnly,)
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class RecipeFavoriteView(BaseRetrieveDestroyViewSetView):
    queryset = Favorite.objects.all()
    serializer_class = MiniRecipeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_model(self):
        return Favorite


class ShoppingCartView(BaseRetrieveDestroyViewSetView):
    queryset = ShoppingCart.objects.all()
    serializer_class = MiniRecipeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_model(self):
        return ShoppingCart


class ShoppingCartListView(ListViewSet):
    queryset = ShoppingCart.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        shopping_cart = (
            ShoppingCart.objects.filter(
                user=request.user,
            )
            .select_related('recipe')
            .prefetch_related('recipe__recipe_ingredients')
        )
        ingredients = defaultdict(int)
        for item in shopping_cart:
            recipe_ingredients = item.recipe.recipe_ingredients.all()
            for ingredient in recipe_ingredients:
                ingredient_key = ingredient.ingredient_id
                ingredients[ingredient_key] += ingredient.amount

        content = 'Ингредиент (единица измерения) - количество\n'
        for ingredient_id, amount in ingredients.items():
            ingredient = Ingredient.objects.get(pk=ingredient_id)
            content += f'● {ingredient.name} ({ingredient.measurement_unit}) - {amount}\n'

        response = HttpResponse(content, content_type='text/plain')
        response[
            'Content-Disposition'
        ] = 'attachment; filename=shopping_cart.txt'
        return response
