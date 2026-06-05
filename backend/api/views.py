# from django.http import JsonResponse
# 
# def index(request):
#     return JsonResponse({'value': 'Hello from Django!'})

# from django.db.models.query import QuerySet
# from django.core.exceptions import BadRequest
from rest_framework import viewsets, filters
from . import models
from . import serializers


class FolderViewSet(viewsets.ModelViewSet):
    """API endpoint that allows folders to be viewed or edited.
    """

    queryset = models.Folder.objects.all()
    serializer_class = serializers.FolderSerializer
    filter_backends = [filters.OrderingFilter]
    filterset_fields = ['parent']
    ordering_fields = ['name', 'parent', ]
    ordering = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.query_params.get('rootonly'):
            queryset = queryset.filter(parent__isnull=True)
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.FolderListSerializer
        return super().get_serializer_class()


class ImageViewSet(viewsets.ModelViewSet):
    """API endpoint that allows images to be viewed or edited.
    """

    queryset = models.Image.objects.all()
    serializer_class = serializers.ImageSerializer
    filter_backends = [filters.OrderingFilter]
    filterset_fields = ['parent']
    ordering_fields = ['name', 'parent', 'timestamp', 'favorite']
    ordering = ['-timestamp']

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.query_params.get('rootonly'):
            queryset = queryset.filter(parent__isnull=True)
        if self.request.query_params.get('favoriteonly'):
            queryset = queryset.filter(favorite__isnull=False)
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.ImageListSerializer
        return super().get_serializer_class()
