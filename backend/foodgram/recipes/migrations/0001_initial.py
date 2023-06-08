# Generated by Django 3.2 on 2023-06-07 19:19

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Favorite',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
            ],
            options={
                'verbose_name': 'избранное',
                'verbose_name_plural': 'избранное',
                'default_related_name': 'favorites',
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'name',
                    models.CharField(max_length=200, verbose_name='название'),
                ),
                (
                    'measurement_unit',
                    models.CharField(
                        max_length=15, verbose_name='единица измерения'
                    ),
                ),
            ],
            options={
                'verbose_name': 'ингредиент',
                'verbose_name_plural': 'ингредиенты',
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'image',
                    models.ImageField(
                        upload_to='recipes/', verbose_name='изображение'
                    ),
                ),
                (
                    'name',
                    models.CharField(max_length=200, verbose_name='название'),
                ),
                ('text', models.TextField(verbose_name='описание')),
                (
                    'cooking_time',
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1)
                        ],
                        verbose_name='время приготовления',
                    ),
                ),
                (
                    'pub_date',
                    models.DateTimeField(
                        auto_now_add=True, verbose_name='дата публикации'
                    ),
                ),
            ],
            options={
                'verbose_name': 'рецепт',
                'verbose_name_plural': 'рецепты',
                'ordering': ('-pub_date',),
                'default_related_name': 'recipes',
            },
        ),
        migrations.CreateModel(
            name='RecipeIngredients',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'amount',
                    models.PositiveIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1)
                        ],
                        verbose_name='количество',
                    ),
                ),
            ],
            options={
                'verbose_name': 'through-модель',
                'verbose_name_plural': 'through-модели',
                'default_related_name': 'recipe_ingredients',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'name',
                    models.CharField(
                        max_length=200, unique=True, verbose_name='название'
                    ),
                ),
                (
                    'color',
                    models.CharField(
                        max_length=7, unique=True, verbose_name='цвет'
                    ),
                ),
                (
                    'slug',
                    models.CharField(
                        max_length=200, unique=True, verbose_name='слаг'
                    ),
                ),
            ],
            options={
                'verbose_name': 'тег',
                'verbose_name_plural': 'теги',
            },
        ),
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'recipe',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='shopping_cart',
                        to='recipes.recipe',
                        verbose_name='рецепт',
                    ),
                ),
            ],
            options={
                'verbose_name': 'список покупок',
                'verbose_name_plural': 'список покупок',
                'default_related_name': 'shopping_cart',
            },
        ),
    ]
