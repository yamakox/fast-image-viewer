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
    favorite = models.DateTimeField(
        blank=False,
        null=True,
    )
