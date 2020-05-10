from django.db import models
from .custom_slugify import slugify


class UniqueSys(models.Model):
    object_name = models.CharField(max_length=100, blank=True, default='user')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)+"->"+self.object_name


class City(models.Model):
    title = models.CharField(max_length=100)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.CASCADE)
    slug = models.SlugField(null=True, blank=True)

    def __str__(self):
        full_path = [self.title]  # post.  use __unicode__ in place of
        # __str__ if you are using python 2
        k = self.parent

        while k is not None:
            full_path.append(k.title)
            k = k.parent

        return ' -> '.join(full_path)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_all_children(self, container=None):
        if container is None:
            container = []
        result = container
        for child in self.children.all():
            result.append(child.pk)
            if child.children.count() > 0:
                child.get_all_children(result)
        return result


class GoalOfSupport(models.Model):
    name = models.CharField(max_length=52,  null=True, blank=True)
    slug = models.SlugField(null=True, blank=True)

    def __str__(self):
        return self.name
