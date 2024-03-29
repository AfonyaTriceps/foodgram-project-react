from django.contrib import admin

from foodgram.admin import BaseAdmin
from users.models import Follow, User


@admin.register(User)
class UserAdmin(BaseAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_filter = ('email', 'username')
    search_fields = ('email', 'username')


@admin.register(Follow)
class FollowAdmin(BaseAdmin):
    list_display = ('id', 'user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')
