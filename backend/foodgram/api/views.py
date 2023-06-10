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
            ShoppingCart.objects.filter(user=request.user)
            .select_related('recipe')
            .prefetch_related('recipe__recipe_ingredients')
        )
        ingredients = []
        for item in shopping_cart:
            for ingredient in item.recipe.recipe_ingredients.all():
                found = False
                for ing in ingredients:
                    if ing['id'] == ingredient.ingredient_id:
                        ing['amount'] += ingredient.amount
                        found = True
                        break
                if not found:
                    ingredients.append(
                        {
                            'id': ingredient.ingredient_id,
                            'amount': ingredient.amount,
                        },
                    )

        line = 'Ингредиент (единица измерения) - количество\n'
        for ingredient in ingredients:
            ing = Ingredient.objects.get(pk=ingredient['id'])
            line += f'● {ing.name} ({ing.measurement_unit}) - {ingredient["amount"]}\n'

        response = HttpResponse(line, content_type='text/plain')
        response[
            'Content-Disposition'
        ] = 'attachment; filename=shopping_cart.txt'
        return response
