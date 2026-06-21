# from django.http import JsonResponse
#
# def index(request):
#     return JsonResponse({'value': 'Hello from Django!'})

# from django.db.models.query import QuerySet
from hashlib import md5
from django.http import HttpResponse, JsonResponse
from django.db.models import DateTimeField, OuterRef, Subquery, Value
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import viewsets, pagination  # , renderers
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework.authentication import SessionAuthentication
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from . import models
from . import serializers
from . import renderers as image_renderers
from . import dataset
import env
from log import logger
from pathlib import Path

root_path = Path(env.FIV_DATASET_FOLDER_PATH).resolve()
appdata_path = Path(env.FIV_APPDATA_FOLDER_PATH).resolve()


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


def _hash_password(password: str) -> str:
    return md5(password.encode()).hexdigest()


def _get_session_user(request) -> models.User | None:
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    try:
        return models.User.objects.get(pk=user_id)
    except models.User.DoesNotExist:
        return None


def _annotate_favorite(queryset, user: models.User | None):
    if user:
        favorite_subquery = models.Favorite.objects.filter(
            image=OuterRef('pk'),
            user=user,
        ).values('timestamp')[:1]
        return queryset.annotate(
            favorite=Subquery(favorite_subquery, output_field=DateTimeField()),
        )
    return queryset.annotate(
        favorite=Value(None, output_field=DateTimeField()),
    )


@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([SessionAuthentication])
def session(request):
    user = _get_session_user(request)
    if not user:
        return Response(
            {'detail': '認証されていません。'},
            status=HTTP_401_UNAUTHORIZED,
        )
    return Response({'id': user.id, 'username': user.username})


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([SessionAuthentication])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
        return Response(
            {'detail': 'ユーザー名とパスワードが必要です。'},
            status=HTTP_400_BAD_REQUEST,
        )
    try:
        user = models.User.objects.get(username=username)
    except models.User.DoesNotExist:
        return Response(
            {'detail': 'ログインに失敗しました。'},
            status=HTTP_401_UNAUTHORIZED,
        )
    if user.password != _hash_password(password):
        return Response(
            {'detail': 'ログインに失敗しました。'},
            status=HTTP_401_UNAUTHORIZED,
        )
    request.session['user_id'] = user.id
    return Response({'id': user.id, 'username': user.username})


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([SessionAuthentication])
def logout(request):
    request.session.flush()
    return Response({'detail': 'ログアウトしました。'})


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([SessionAuthentication])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
        return Response(
            {'detail': 'ユーザー名とパスワードが必要です。'},
            status=HTTP_400_BAD_REQUEST,
        )
    if models.User.objects.filter(username=username).exists():
        return Response(
            {'detail': 'このユーザー名は既に使用されています。'},
            status=HTTP_400_BAD_REQUEST,
        )
    user = models.User.objects.create(
        username=username,
        password=_hash_password(password),
    )
    return Response(
        {'id': user.id, 'username': user.username},
        status=HTTP_201_CREATED,
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

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = _get_session_user(self.request)
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        user = _get_session_user(self.request)
        queryset = _annotate_favorite(queryset, user)
        if self.request.query_params.get('rootonly'):
            queryset = queryset.filter(parent__isnull=True)
        if self.request.query_params.get('favoriteonly'):
            if user:
                queryset = queryset.filter(favorites__user=user).distinct()
            else:
                queryset = queryset.none()
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
        user = _get_session_user(request)
        if not user:
            return Response(
                {'detail': '認証されていません。'},
                status=HTTP_401_UNAUTHORIZED,
            )
        image = self.__get_image_record(pk)
        if image is None:
            return _make_404_response(detail='Image data not found.')
        if 'favorite' not in request.data:
            raise ValidationError({'favorite': 'This field is required.'})

        favorite_value = request.data.get('favorite')
        if favorite_value is None:
            models.Favorite.objects.filter(user=user, image=image).delete()
            return Response({'id': image.id, 'favorite': None})

        timestamp = parse_datetime(favorite_value) if isinstance(favorite_value, str) else favorite_value
        if timestamp is None:
            timestamp = timezone.now()
        favorite, _created = models.Favorite.objects.update_or_create(
            user=user,
            image=image,
            defaults={'timestamp': timestamp},
        )
        return Response({'id': image.id, 'favorite': favorite.timestamp})

    @action(methods=['get'], detail=True, renderer_classes=[image_renderers.JPEGRenderer])
    def image(self, request, pk=None):
        logger.debug(f'image: {pk=} {request=}')
        return self.__retrieve_image(request, pk)

    @action(methods=['get'], detail=True, renderer_classes=[image_renderers.JPEGRenderer])
    def thumbnail(self, request, pk=None):
        logger.debug(f'image: {pk=} {request=}')
        try:
            with dataset.Hdf5File(appdata_path) as hdf5file:
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
