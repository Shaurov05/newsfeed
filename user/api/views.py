from rest_framework import generics, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from user.api.permissions import IsOwnProfileOrReadOnly, IsOwnerOrReadOnly


from user.models import *
from user.api.serializers import *


class NewsFeedViewSet(ModelViewSet):
    # user_profile =
    queryset = NewsFeed.objects.all()
    serializer_class = NewsFeedSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


