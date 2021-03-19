from django.urls import path, include
from user.api.views import *

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"profiles", ProfileStatusViewSet)


