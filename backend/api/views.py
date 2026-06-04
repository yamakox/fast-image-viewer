# from django.http import JsonResponse
# 
# def index(request):
#     return JsonResponse({'value': 'Hello from Django!'})

from django.db.models.query import QuerySet
from django.core.exceptions import BadRequest
from rest_framework import viewsets, filters
from . import models
from . import serializers


class FolderViewSet(viewsets.ModelViewSet):
    """API endpoint that allows folders to be viewed or edited.
    """

    queryset = models.Folder.objects.all().order_by('name')
    serializer_class = serializers.FolderSerializer
    filterset_fields = ['parent']

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.query_params.get('rootonly'):
            queryset = queryset.filter(parent__isnull=True)
        return queryset


class ImageViewSet(viewsets.ModelViewSet):
    """API endpoint that allows images to be viewed or edited.
    """

    queryset = models.Image.objects.all().order_by('-timestamp')
    serializer_class = serializers.ImageSerializer
    filterset_fields = ['parent']

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.query_params.get('rootonly'):
            queryset = queryset.filter(parent__isnull=True)
        return queryset
