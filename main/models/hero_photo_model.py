"""
Hero Photo model for the auto-scrolling gallery in the hero section of the homepage.
Admins can upload and manage photos (office, MoU signings, client visits, etc.)
"""

from django.db import models
import time


def upload_hero_photo(instance, filename):
    """Custom upload path for hero photos."""
    ext = filename.split('.')[-1]
    timestamp = str(int(time.time() * 1000))[-10:]
    return f'hero/{timestamp}.{ext}'


class HeroPhoto(models.Model):
    """Photo displayed in the auto-scrolling gallery on the homepage hero section."""

    image = models.ImageField(
        upload_to=upload_hero_photo,
        help_text="Photo for the hero gallery (recommended: 800x600px or similar landscape)"
    )
    caption = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Optional short caption shown on hover (e.g., 'MoU Signing Ceremony')"
    )
    display_order = models.IntegerField(
        default=0,
        help_text="Lower numbers appear first"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Only active photos are shown on the website"
    )

    created_at = models.BigIntegerField(editable=False)

    class Meta:
        db_table = 'hero_photos'
        ordering = ['display_order', 'id']
        verbose_name = 'Hero Photo'
        verbose_name_plural = 'Hero Photos'

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = int(time.time() * 1000)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.caption or f"Hero Photo #{self.id}"
