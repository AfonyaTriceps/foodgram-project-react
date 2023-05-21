from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator


User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField('название', max_length=200)
    measurement_unit = models.CharField('единица измерения', max_length=15)

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField('название', max_length=200, unique=True)
    color = models.CharField('цвет', max_length=7, unique=True)
    slug = models.CharField('слаг', max_length=200, unique=True)

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    ingredients = models.ManyToManyField(Ingredient, verbose_name='ингредиенты')
    tags = models.ManyToManyField(Tag, verbose_name='теги')
    image = models.ImageField('изображение', upload_to='recipes/')
    name = models.CharField('название', max_length=200)
    text = models.TextField('описание')
    cooking_time = models.PositiveSmallIntegerField('время приготовления', validators=(MinValueValidator(1),),)
    pub_date = models.DateTimeField('дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        default_related_name = 'recipes'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name='рецепт',)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, verbose_name='ингредиент')
    amount = models.PositiveIntegerField('количество', validators=(MinValueValidator(1),),)

    class Meta:
        verbose_name = 'through-модель'
        verbose_name_plural = 'through-модели'

    def __str__(self):
        return f'{self.recipe} содержит {self.ingredient} в количестве {self.amount}'
