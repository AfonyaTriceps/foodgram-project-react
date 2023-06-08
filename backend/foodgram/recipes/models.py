from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class NameModel(models.Model):
    name = models.CharField('название', max_length=200)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Ingredient(NameModel):
    measurement_unit = models.CharField('единица измерения', max_length=15)

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'


class Tag(NameModel):
    color = models.CharField('цвет', max_length=7, unique=True)
    slug = models.CharField('слаг', max_length=200, unique=True)

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'


class Recipe(NameModel):
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredients',
        verbose_name='ингредиенты',
    )
    tags = models.ManyToManyField(Tag, verbose_name='теги')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
    )
    image = models.ImageField('изображение', upload_to='recipes/')
    text = models.TextField('описание')
    cooking_time = models.PositiveSmallIntegerField(
        'время приготовления',
        validators=(MinValueValidator(1),),
    )
    pub_date = models.DateTimeField('дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        default_related_name = 'recipes'
        ordering = ('-pub_date',)


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='ингредиент',
    )
    amount = models.PositiveIntegerField(
        'количество',
        validators=(MinValueValidator(1),),
    )

    class Meta:
        verbose_name = 'through-модель'
        verbose_name_plural = 'through-модели'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_ingredients_in_recipes',
            ),
        ]
        default_related_name = 'recipe_ingredients'

    def __str__(self):
        return f'{self.recipe} содержит {self.ingredient}({self.amount} шт.)'


class UserRecipeModel(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт',
    )

    class Meta:
        abstract = True


class Favorite(UserRecipeModel):
    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'избранное'
        default_related_name = 'favorites'

        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_recipe',
            ),
        )

    def __str__(self):
        return f'Рецепт {self.recipe} в избранном у {self.user}'


class ShoppingCart(UserRecipeModel):
    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'список покупок'
        default_related_name = 'shopping_cart'

        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_list_recipe',
            ),
        )

    def __str__(self):
        return f'Рецепт {self.recipe} в списке покупок у {self.user}'
