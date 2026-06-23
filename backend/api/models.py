from django.conf import settings
from django.db import models


class Folder(models.Model):
    name = models.TextField()
    pathname = models.TextField()
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='children',
    )


class Image(models.Model):
    name = models.TextField()
    parent = models.ForeignKey(
        Folder,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='images',
    )
    hash = models.CharField(max_length=16)
    timestamp = models.DateTimeField()


class Favorite(models.Model):
    timestamp = models.DateTimeField()
    image = models.ForeignKey(
        Image,
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'image'],
                name='unique_user_image_favorite',
            ),
        ]
