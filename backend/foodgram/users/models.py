from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
    )
    email = models.EmailField(
        'почта',
        max_length=254,
        unique=True,
        help_text='Укажите email пользователя',
    )
    username = models.CharField(
        'имя пользователя',
        max_length=100,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Недопустимый формат имени пользователя',
            ),
        ],
    )
    first_name = models.CharField('имя', max_length=150, blank=True)
    last_name = models.CharField('фамилия', max_length=150, blank=True)

    class Meta:
        ordering = ('email',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.email


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='автор',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscription',
            ),
        ]
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        ordering = ('-id',)

    def __str__(self):
        return f'Пользователь {self.user} подписан на {self.author}'
