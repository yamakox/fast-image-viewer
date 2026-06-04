from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('folders', views.FolderViewSet)
router.register('images', views.ImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
