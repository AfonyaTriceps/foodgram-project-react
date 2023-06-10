from django.urls import include, path
from djoser.views import UserViewSet
from rest_framework.routers import DefaultRouter

from users.views import FollowListView, FollowView

app_name = 'users'

router = DefaultRouter()
router.register('users', UserViewSet)


authurlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

urlpatterns = [
    path(
        'users/<int:pk>/subscribe/',
        FollowView.as_view(),
        name='subscribe',
    ),
    path(
        'users/subscriptions/',
        FollowListView.as_view(),
        name='subscriptions',
    ),
    path('', include(router.urls)),
]

urlpatterns += authurlpatterns
