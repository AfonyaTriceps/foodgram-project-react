from rest_framework import generics, mixins, viewsets


class RetrieveListViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    pass


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
