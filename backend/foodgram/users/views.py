from djoser.views import UserViewSet
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from api.pagination import LimitPageNumberPagination
from api.serializers import FollowSerializer
from users.models import Follow, User
from users.serializers import CustomUserSerializer


class UsersView(UserViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = LimitPageNumberPagination
    serializer_class = CustomUserSerializer
    queryset = User.objects.all()

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, pk=id)
        if request.method == 'POST':
            if author == request.user:
                raise serializers.ValidationError(
                    'Нельзя подписаться на самого себя',
                )
            Follow.objects.create(user=request.user, author=author)
            return Response(
                {'detail': 'Вы подписались на пользователя.'},
                status=status.HTTP_201_CREATED,
            )

        if request.method == 'DELETE':
            follower = get_object_or_404(Follow, user=request.user, author=author).delete()
            follower.delete()
            return Response(
                {'detail': 'Вы отписались от пользователя.'},
                status=status.HTTP_204_NO_CONTENT,
            )

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        queryset = Follow.objects.filter(user=request.user)
        pages_queryset = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages_queryset,
            many=True,
            context={'request': request},
        )
        return self.get_paginated_response(serializer.data)
