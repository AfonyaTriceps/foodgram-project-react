from django.conf import settings
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from api.fields import Hex2NameColor
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCart,
    Tag,
)
from users.models import Follow
from users.serializers import CustomUserSerializer


class MiniRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def validate(self, data):
        user = self.context.get('request').user
        author_id = self.context.get('view').kwargs.get('pk')
        if user.id == author_id:
            raise serializers.ValidationError(
                'Вы не можете подписаться на себя!',
            )
        if user.following.filter(author_id=author_id).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя!',
            )
        return data

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.author.following.filter(user=user).exists()
        return False

    def get_recipes(self, obj):
        recipes_limit = self.context.get('request').query_params.get(
            'recipes_limit',
        )
        recipes = obj.author.recipes.all()
        if recipes_limit:
            recipes = recipes[: int(recipes_limit)]
        serializer = MiniRecipeSerializer(
            recipes,
            many=True,
        )
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.author.recipes.all().count()


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('amount',)


class RecipeWriteIngredients(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')

    def validate_amount(self, amount):
        if int(amount) < settings.MIN_FIELD_RESTRICTION:
            raise serializers.ValidationError(
                'Количество ингредиента должно быть больше 0!',
            )
        if int(amount) > settings.MAX_FIELD_RESTRICTION:
            raise serializers.ValidationError(
                'Количество ингредиента должно быть больше 32000!',
            )
        return amount


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = RecipeIngredientsSerializer(
        many=True,
        source='recipe_ingredients',
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = (
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_obj(self, obj, model):
        user = self.context.get('request').user
        if user.is_authenticated:
            return model.objects.filter(user=user, recipe_id=obj.id).exists()
        return False

    def get_is_favorited(self, obj):
        return self.get_obj(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self.get_obj(obj, ShoppingCart)


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeWriteIngredients(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_cooking_time(self, cooking_time):
        if int(cooking_time) < settings.MIN_FIELD_RESTRICTION:
            raise serializers.ValidationError(
                'Время должно быть больше 0!',
            )
        if int(cooking_time) > settings.MAX_FIELD_RESTRICTION:
            raise serializers.ValidationError(
                'Время должно быть до 32000!',
            )
        return cooking_time

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Необходимо указать хотя бы один ингредиент.',
            )
        ingredient_set = set()
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredient_set:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться.',
                )
            ingredient_set.add(ingredient_id)
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError('Рецепт не может быть без тега!')
        if len(set(tags)) != len(tags):
            raise serializers.ValidationError('Теги не должны повторяться.')
        return tags

    def create_ingredients_for_recipe(self, ingredients, recipe):
        recipe_ingredients = [
            RecipeIngredients(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount'],
            )
            for ingredient in ingredients
        ]
        RecipeIngredients.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients_for_recipe(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.set(tags)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time,
        )
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        RecipeIngredients.objects.filter(recipe=instance).delete()
        self.create_ingredients_for_recipe(ingredients, instance)
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data
