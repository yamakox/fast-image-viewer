from rest_framework import serializers
from . import models


class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Folder
        fields = ['name', 'pathname', 'parent']


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Image
        fields = ['name', 'parent', 'timestamp', 'favorite']
