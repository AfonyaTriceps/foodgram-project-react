from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, serializers, status, viewsets
from rest_framework.response import Response

from recipes.models import Recipe


class RetrieveListViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    pass


class BaseRetrieveDestroyViewSetView(
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        model = self.get_model()
        if model.objects.filter(user=request.user, recipe=recipe).exists():
            raise serializers.ValidationError('Рецепт уже добавлен.')

        model.objects.create(user=request.user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        model = self.get_model()
        try:
            model.objects.get(user=request.user, recipe=pk).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except model.DoesNotExist:
            return Response(
                {'detail': 'Вы не подписаны на этого пользователя!'},
                status=status.HTTP_404_NOT_FOUND,
            )

    def get_model(self):
        raise NotImplementedError('Необходимо определить "get_model".')


class CreateDestroyListViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    pass


class ListViewSet(
    mixins.ListModelMixin,
    generics.GenericAPIView,
):
    pass
