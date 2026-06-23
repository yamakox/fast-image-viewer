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
    favorite = serializers.SerializerMethodField()

    class Meta:
        model = models.Image
        fields = ['id', 'name', 'parent', 'hash', 'timestamp', 'favorite']

    def get_favorite(self, obj: models.Image):
        user = self.context.get('user')
        if not user:
            return None
        favorite = models.Favorite.objects.filter(user=user, image=obj).first()
        return favorite.timestamp if favorite else None


class ImageListSerializer(ImageSerializer):
    class Meta(ImageSerializer.Meta):
        fields = ['id', 'name', 'favorite']
