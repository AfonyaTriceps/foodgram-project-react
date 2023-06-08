import csv

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов из csv файла'

    def handle(self, *args, **kwargs):
        data_path = settings.BASE_DIR
        with open(
            f'{data_path}/data/ingredients.csv',
            'r',
            encoding='utf-8',
        ) as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                name, measurement_unit = row
                Ingredient.objects.create(
                    name=name,
                    measurement_unit=measurement_unit,
                )
        self.stdout.write(self.style.SUCCESS('Все ингредиенты загружены!'))
