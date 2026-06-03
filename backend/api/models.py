from django.db import models

class Folder(models.Model):
    path = models.TextField()
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True, 
        related_name='children'
    )

class Image(models.Model):
    name = models.TextField()
    parent = models.ForeignKey(
        Folder, 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True, 
        related_name='images'
    )
    hash = models.CharField(max_length=16)
    timestamp = models.DateTimeField('timestamp')
