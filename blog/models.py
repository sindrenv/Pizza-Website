from django.db import models

from django.contrib.auth.models import User


# Create your models here.
class Category(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class Status(models.Model):
    title = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.title

class Post(models.Model):
    title = models.CharField(max_length=150)
    author = models.CharField(max_length=100) 
    published = models.CharField(max_length=100)
    content = models.TextField (blank=True, null=True)
    status = models.ForeignKey("Status", models.PROTECT)
    categories = models.ManyToManyField("Category", related_name="posts")
        class Meta:
            ordering = ["-published"]

        def __str__(self):
            return f"{self.author}: {self.title}"