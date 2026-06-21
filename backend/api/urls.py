from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter(trailing_slash=False)  # URL末尾の`/`は無しにする
router.register('folders', views.FolderViewSet)
router.register('images', views.ImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('session', views.session),
    path('login', views.login),
    path('logout', views.logout),
    path('register', views.register),
]
