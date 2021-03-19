from rest_framework import generics, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from user.api.permissions import IsOwnProfileOrReadOnly, IsGetRequest
from rest_framework.response import Response

from user.models import *
from user.api.serializers import *


class NewsFeedViewSet(ModelViewSet):
    serializer_class = NewsFeedSerializer
    permission_classes = [IsAuthenticated, IsGetRequest]

    def get_queryset(self):
        userProfile = UserProfile.objects.get(user=self.request.user)
        queryset = NewsFeed.objects.filter(user=userProfile)
        return queryset


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserProfileViewSet(ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsGetRequest]










