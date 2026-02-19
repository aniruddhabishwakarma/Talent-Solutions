"""
Team Member model for the "Our Team" section on the homepage.
Admins can manage team members via the admin panel.
"""

from django.db import models
from django.utils.text import slugify
import time


def upload_team_photo(instance, filename):
    """Custom upload path for team member photos."""
    ext = filename.split('.')[-1]
    timestamp = str(int(time.time() * 1000))[-8:]
    return f'team/{instance.id or "new"}_{slugify(instance.name)}_{timestamp}.{ext}'


class TeamMember(models.Model):
    """Team member displayed on the homepage team section."""

    name = models.CharField(max_length=100, help_text="Full name of the team member")
    position = models.CharField(max_length=150, help_text="Job title/role")
    bio = models.TextField(help_text="Biography")
    photo = models.ImageField(
        upload_to=upload_team_photo,
        help_text="Team member photo (recommended: square image, min 400x400px)"
    )

    # Social media links (optional)
    facebook_url = models.URLField(max_length=200, blank=True, null=True)
    instagram_url = models.URLField(max_length=200, blank=True, null=True)
    whatsapp_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="WhatsApp number with country code (e.g., +9779841234567)"
    )

    # Display settings
    display_order = models.IntegerField(
        default=0,
        help_text="Lower numbers appear first (0, 1, 2, ...)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Only active members are shown on the website"
    )

    # Timestamps
    created_at = models.BigIntegerField(editable=False)
    updated_at = models.BigIntegerField()

    class Meta:
        db_table = 'team_members'
        ordering = ['display_order', 'id']
        verbose_name = 'Team Member'
        verbose_name_plural = 'Team Members'

    def save(self, *args, **kwargs):
        now = int(time.time() * 1000)
        if not self.created_at:
            self.created_at = now
        self.updated_at = now
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.position}"

    @property
    def whatsapp_url(self):
        """Generate WhatsApp click-to-chat URL."""
        if self.whatsapp_number:
            # Remove any spaces, dashes, or special chars
            clean_number = ''.join(filter(str.isdigit, self.whatsapp_number))
            if not clean_number.startswith('+'):
                clean_number = '+' + clean_number
            return f"https://wa.me/{clean_number}"
        return None
