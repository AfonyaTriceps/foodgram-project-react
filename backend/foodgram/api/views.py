import codecs
import csv
from collections import defaultdict

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import LimitPageNumberPagination
from api.permissions import IsAuthorAdminOrReadOnly
from api.serializers import (
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    ShortRecipeSerializer,
    TagSerializer,
)
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.AllowAny,)
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (permissions.AllowAny,)
    pagination_class = None
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorAdminOrReadOnly,)
    pagination_class = LimitPageNumberPagination
    queryset = Recipe.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def favorite_and_shopping_cart_actions(self, request, pk, model):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            serializer = ShortRecipeSerializer(
                recipe,
                request.data,
                context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            if model.objects.filter(user=request.user, recipe__id=pk).exists():
                return Response(
                    {'errors': 'Рецепт уже добавлен!'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            model.objects.create(user=request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            obj = get_object_or_404(model, user=request.user, recipe=recipe)
            obj.delete()
            return Response(
                {'detail': 'Рецепт удален.'},
                status=status.HTTP_204_NO_CONTENT,
            )

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        return self.favorite_and_shopping_cart_actions(request, pk, Favorite)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        return self.favorite_and_shopping_cart_actions(
            request,
            pk,
            ShoppingCart,
        )

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
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
                key = ingredient.ingredient_id
                ingredients[key] += ingredient.amount

        with codecs.open('shopping_cart.csv', 'w', 'utf-8-sig') as file:
            writer = csv.writer(file, dialect='excel')
            writer.writerow(['Ингредиент (единица измерения) - количество'])

            for ingredient_id, amount in ingredients.items():
                ingredient = Ingredient.objects.get(pk=ingredient_id)
                writer.writerow(
                    [
                        f'{ingredient.name} ({ingredient.measurement_unit}) - {amount}',
                    ],
                )
        return FileResponse(
            open('shopping_cart.csv', 'rb'),
            as_attachment=True,
        )
