from django.db import models
from django.utils.text import slugify
import time


class Skill(models.Model):
    """Model for job skills."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    created_at = models.BigIntegerField(editable=False)

    class Meta:
        db_table = 'skills'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Auto-generate slug
        if not self.slug:
            self.slug = slugify(self.name)

        # Set created_at on first save (epoch milliseconds)
        if not self.created_at:
            self.created_at = int(time.time() * 1000)

        super().save(*args, **kwargs)
