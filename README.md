# Проект YaMDb

![example workflow](https://github.com/AfonyaTriceps/foodgram-project-react/actions/workflows/main.yml/badge.svg)

* Проект YaMDb собирает рецепты пользователей.
* Рецепты делятся на различные теги.
* Произведению может быть присвоен жанр из списка предустановленных.
* Добавлять теги и ингредиенты может только администратор.
* Публиковать свои рецепты могут только авторизированные пользователи.
* Пользователи могут добавлять рецепт в избранное и подписываться на
других авторов.
* Сервис «Список покупок» позволяет пользователям создавать список
продуктов, которые нужно купить для приготовления выбранных блюд.
* Сформированный список покупок можно скачать в текстовом формате.

### URL's

- http://62.84.123.80/

### Как запустить проект

> команды указаны для Windows
Клонировать репозиторий и далее перейти в него.

```bash
git clone git@github.com:AfonyaTriceps/foodgram-project-react.git
```

Переходим в папку с файлом docker-compose.yaml:

```bash
cd infra
```

Запустить контейнеры:

```bash
docker-compose up -d --build
```

Выполнить миграции:

```bash
docker-compose exec backend python manage.py migrate
```

Создать суперпользователя:

```bash
docker-compose exec backend python manage.py createsuperuser
```

Собрать статику:

```bash
docker-compose exec backend python manage.py collectstatic --no-input
```

Остановить контейнеры:

```bash
docker-compose down -v
```

## Описание команды для заполнения БД данными из csv

```bash
docker-compose exec backed python manage.py load_data
```

### Для создания .env выполните

```bash
cp .env.example .env
```

### Документация API YaMDb

С полной документацией можно ознакомиться по адресу
[http://localhost:8000/redoc/](http://localhost:8000/redoc/)
