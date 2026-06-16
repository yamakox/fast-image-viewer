# from django.http import JsonResponse
#
# def index(request):
#     return JsonResponse({'value': 'Hello from Django!'})

# from django.db.models.query import QuerySet
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets, pagination  # , renderers
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from . import models
from . import serializers
from . import renderers as image_renderers
from . import dataset
import env
from log import logger
from pathlib import Path

root_path = Path(env.FIV_DATASET_FOLDER_PATH).resolve()
appdata_path = Path(env.FIV_APPDATA_FOLDER_PATH).resolve()
hdf5file = dataset.Hdf5File(appdata_path)


def _make_400_response(**kwargs) -> JsonResponse:
    return JsonResponse(
        dict(**kwargs),
        status=HTTP_400_BAD_REQUEST,
    )


def _make_404_response(**kwargs) -> JsonResponse:
    return JsonResponse(
        dict(**kwargs),
        status=HTTP_404_NOT_FOUND,
    )


def _make_500_response(**kwargs) -> JsonResponse:
    return JsonResponse(
        dict(**kwargs),
        status=HTTP_500_INTERNAL_SERVER_ERROR,
    )


class FolderViewSet(viewsets.ModelViewSet):
    """API endpoint that allows folders to be viewed or edited."""

    http_method_names = ['get', 'head', 'options']
    queryset = models.Folder.objects.all()
    serializer_class = serializers.FolderSerializer
    filterset_fields = ['parent']
    ordering_fields = [
        'name',
        'parent',
    ]
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
        return Response(
            {
                'count': self.page.paginator.count,
                'page': self.page.number,
                'num_pages': self.page.paginator.num_pages,
                'page_size': self.page_size,
                'results': data,
            }
        )


class ImageViewSet(viewsets.ModelViewSet):
    """API endpoint that allows images to be viewed or edited."""

    http_method_names = ['get', 'patch', 'head', 'options']
    # renderer_classes = [image_renderers.JPEGRenderer, renderers.JSONRenderer, renderers.BrowsableAPIRenderer]
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

    def retrieve(self, request, pk=None):
        logger.debug(f'retrieve: {pk=} {request=}')
        # if request.accepted_media_type.startswith('image/'):
        #     return self.__retrieve_image(request, pk)
        return super().retrieve(request, pk)

    def partial_update(self, request, pk=None):
        image = self.__get_image_record(pk)
        if image is None:
            return _make_404_response(detail='Image data not found.')
        serializer = serializers.ImageSerializer(image, request.data, partial=True)
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)
        serializer.save()
        return Response(
            {
                'id': image.id,
                'favorite': image.favorite,
            }
        )

    @action(methods=['get'], detail=True, renderer_classes=[image_renderers.JPEGRenderer])
    def image(self, request, pk=None):
        logger.debug(f'image: {pk=} {request=}')
        return self.__retrieve_image(request, pk)

    @action(methods=['get'], detail=True, renderer_classes=[image_renderers.JPEGRenderer])
    def thumbnail(self, request, pk=None):
        logger.debug(f'image: {pk=} {request=}')
        try:
            # hdf5file = dataset.Hdf5File(appdata_path)
            if not hdf5file.has_data(pk):
                return _make_404_response(detail='Thumbnail image not found.')
            bindata = hdf5file.get_data(pk)
        except Exception as excep:
            return JsonResponse(
                {'id': pk, 'error': str(excep)},
                status=HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # NOTE: Response(bindata, ...)ではブラウザに画像を送信できなかった(原因不明)
        response = HttpResponse(bindata, content_type=image_renderers.JPEGRenderer.media_type)
        response['Content-Length'] = len(bindata)
        return response

    def __retrieve_image(self, request, pk):
        image = self.__get_image_record(pk)
        if image is None:
            return _make_404_response(detail='Image data not found.')
        if image.parent:
            image_filepath = root_path / image.parent.pathname / image.name
        else:
            image_filepath = root_path / image.name
        if not image_filepath.exists():
            return _make_404_response(detail='Image file not found.', file=str(image_filepath))

        renderer = image_renderers.find_renderer(image_filepath)
        if not renderer:
            return _make_500_response(detail='Unsupported image format: ' + image_filepath.name)
        self.request.accepted_renderer = renderer

        with open(image_filepath, 'rb') as f:
            bindata = f.read()

        # NOTE: Response(bindata, ...)ではブラウザに画像を送信できなかった(原因不明)
        response = HttpResponse(bindata, content_type=renderer.media_type)
        response['Content-Length'] = len(bindata)
        return response

    def __get_image_record(self, pk) -> models.Image | None:
        if not str(pk).isnumeric():
            return None
        images = models.Image.objects.filter(id=pk)
        if not images:
            return None
        return images[0]
