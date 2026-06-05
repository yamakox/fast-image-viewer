from rest_framework import serializers
from . import models


class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Folder
        fields = ['id', 'name', 'pathname', 'parent']


class FolderListSerializer(FolderSerializer):
    class Meta(FolderSerializer.Meta):
        fields = ['id', 'name']


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Image
        fields = ['id', 'name', 'parent', 'hash', 'timestamp', 'favorite']


class ImageListSerializer(ImageSerializer):
    class Meta(ImageSerializer.Meta):
        fields = ['id', 'name', 'favorite']
