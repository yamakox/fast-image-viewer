"""
URL configuration for fast_image_viewer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api-auth/", include("rest_framework.urls", namespace='rest_framework')),
    path('api/v1/', include('api.urls'))
]

# https://docs.djangoproject.com/ja/6.0/ref/contrib/staticfiles/#static-file-development-view
# settings.DEBUGがTrueの場合、STATIC_URL用のURLパターンが追加される
urlpatterns += staticfiles_urlpatterns()
