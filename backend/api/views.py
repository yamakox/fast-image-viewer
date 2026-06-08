# from django.http import JsonResponse
# 
# def index(request):
#     return JsonResponse({'value': 'Hello from Django!'})

# from django.db.models.query import QuerySet
# from django.core.exceptions import BadRequest
from rest_framework import viewsets, filters, pagination
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
# from rest_framework.status import HTTP_204_NO_CONTENT
from . import models
from . import serializers
import env


class FolderViewSet(viewsets.ModelViewSet):
    """API endpoint that allows folders to be viewed or edited.
    """

    http_method_names = ['get', 'head', 'options']
    queryset = models.Folder.objects.all()
    serializer_class = serializers.FolderSerializer
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


class ImageResultsSetPagination(pagination.PageNumberPagination):
    page_size = env.PAGINATION_SIZE
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'page': self.page.number,
            'num_pages': self.page.paginator.num_pages,
            'page_size': self.page_size,
            'results': data,
        })

class ImageViewSet(viewsets.ModelViewSet):
    """API endpoint that allows images to be viewed or edited.
    """

    http_method_names = ['get', 'patch', 'head', 'options']
    queryset = models.Image.objects.all()
    serializer_class = serializers.ImageSerializer
    pagination_class = ImageResultsSetPagination
    filterset_fields = ['parent']
    ordering_fields = ['name', 'parent', 'timestamp', 'favorite']
    ordering = ['-timestamp']
    permission_classes = [AllowAny]

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

    def partial_update(self, request, pk=None):
        image = models.Image.objects.get(pk=pk)
        serializer = serializers.ImageSerializer(image, request.data, partial=True)
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)
        serializer.save()
        return Response({
            'id': image.id, 
            'favorite': image.favorite,
        })
