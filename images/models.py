from django.db import models
import os
from unique.models import UniqueSys


def get_image_path(instance, filename):
    return os.path.join('photos', str(instance.id), filename)


class Image(models.Model):
    path = models.ImageField(upload_to='images/', blank=True, null=True)
    unique = models.ForeignKey(UniqueSys, on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.path.name
