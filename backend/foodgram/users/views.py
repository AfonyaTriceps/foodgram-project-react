from django.shortcuts import get_object_or_404
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

    def post(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, author_id=pk)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        get_object_or_404(Follow, user=request.user, author_id=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowListView(ListViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FollowSerializer
    pagination_class = CustomPageNumberPagination
    queryset = Follow.objects.all()

    def get_queryset(self):
        return self.request.user.follower.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
