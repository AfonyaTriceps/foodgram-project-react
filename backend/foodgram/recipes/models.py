from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from users.models import User


class NameModel(models.Model):
    name = models.CharField('название', max_length=200, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Tag(NameModel):
    color = models.CharField('цвет в HEX', max_length=7, unique=True)
    slug = models.CharField(
        'уникальный слаг',
        max_length=200,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message='Недопустимый формат слага',
            ),
        ],
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'
        ordering = ('name',)


class Ingredient(NameModel):
    measurement_unit = models.CharField('единица измерения', max_length=200)

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'
        ordering = ('name',)


class Recipe(NameModel):
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredients',
        verbose_name='список ингредиентов',
    )
    tags = models.ManyToManyField(Tag, verbose_name='список id тегов')
    image = models.ImageField('картинка', upload_to='recipes/media/')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
    )
    text = models.TextField('описание')
    cooking_time = models.PositiveSmallIntegerField(
        'время приготовления (в минутах)',
        validators=(MinValueValidator(settings.MIN_FIELD_RESTRICTION),),
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        default_related_name = 'recipes'
        ordering = ('-id',)


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
        validators=(MinValueValidator(settings.MIN_FIELD_RESTRICTION),),
    )

    class Meta:
        verbose_name = 'through-модель ингредиентов в рецепте'
        verbose_name_plural = 'through-модели ингредиентов в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_ingredients',
            ),
        ]
        default_related_name = 'recipe_ingredients'
        ordering = ('-id',)

    def __str__(self):
        return f'В рецепте {self.recipe} содержится {self.ingredient}'


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
                name='unique_favorite',
            ),
        )

    ordering = ('-id',)

    def __str__(self):
        return f'{self.user} добавил рецепт {self.recipe} в избранное'


class ShoppingCart(UserRecipeModel):
    class Meta:
        verbose_name = 'покупка'
        verbose_name_plural = 'покупки'
        default_related_name = 'shopping_cart'

        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_list_recipe',
            ),
        )
        ordering = ('-id',)

    def __str__(self):
        return f'Рецепт {self.recipe} в списке покупок у {self.user}'
