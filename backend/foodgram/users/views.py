from rest_framework import permissions, status
from rest_framework.response import Response

from api.mixins import CreateDestroyListViewSet, ListViewSet
from api.pagination import CustomPageNumberPagination
from api.serializers import FollowSerializer
from users.models import Follow


class FollowView(CreateDestroyListViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = None

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if request.user.id == kwargs.get('pk'):
            return Response(
                {'detail': 'Вы не можете подписаться на себя!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if Follow.objects.filter(
            user=request.user,
            author_id=kwargs.get('pk'),
        ).exists():
            return Response(
                {'detail': 'Вы уже подписаны на этого пользователя!'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save(user=request.user, author_id=kwargs.get('pk'))
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, **kwargs):
        try:
            Follow.objects.get(
                user=request.user,
                author_id=kwargs.get('pk'),
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Follow.DoesNotExist:
            return Response(
                {'detail': 'Вы не подписаны на этого пользователя!'},
                status=status.HTTP_404_NOT_FOUND,
            )


class FollowListView(ListViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FollowSerializer
    pagination_class = CustomPageNumberPagination
    queryset = Follow.objects.all()

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
