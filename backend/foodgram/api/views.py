from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.mixins import RetrieveListViewSet
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

    def create_delete_for_favorite_or_shop_cart(self, request, model, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            serializer = MiniRecipeSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            if model.objects.filter(user=request.user, recipe=recipe).exists():
                raise serializers.ValidationError('Рецепт уже добавлен.')

            model.objects.create(user=request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(model, user=request.user, recipe=pk).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, pk):
        return self.create_delete_for_favorite_or_shop_cart(
            request,
            Favorite,
            pk,
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        return self.create_delete_for_favorite_or_shop_cart(
            request,
            ShoppingCart,
            pk,
        )

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        shopping_cart = (
            ShoppingCart.objects.filter(user=request.user)
            .select_related('recipe')
            .prefetch_related('recipe__recipe_ingredients')
        )
        ingredients = {}
        for item in shopping_cart:
            for ingredient in item.recipe.recipe_ingredients.all():
                ingredient_id = ingredient.ingredient_id
                if ingredient_id in ingredients:
                    ingredients[ingredient_id] += ingredient.amount
                else:
                    ingredients[ingredient_id] = ingredient.amount

        line = 'Ингредиент (единица измерения) - количество\n'
        for ingredient_id, amount in ingredients.items():
            ing = Ingredient.objects.get(pk=ingredient_id)
            line += f'● {ing.name} ({ing.measurement_unit}) - {amount}\n'

        response = HttpResponse(line, content_type='text/plain')
        response[
            'Content-Disposition'
        ] = 'attachment; filename=shopping_cart.txt'
        return response
