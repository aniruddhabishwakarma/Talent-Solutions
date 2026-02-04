from django.db import models
from django.contrib.auth.models import AbstractUser
import os
import uuid


def upload_profile_picture(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    unique = uuid.uuid4().hex[:8]
    return f"profile_pictures/{instance.id}_profile_{unique}{ext}"


class User(AbstractUser):
    """
    Custom User model with role-based access control.
    Roles: admin, user
    """

    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]

    AUTH_PROVIDER_CHOICES = [
        ('email', 'Email'),
        ('google', 'Google'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user',
        help_text='User role in the system'
    )
    auth_provider = models.CharField(
        max_length=20,
        choices=AUTH_PROVIDER_CHOICES,
        default='email',
        help_text='Authentication provider used for registration'
    )
    google_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True,
        help_text='Google OAuth unique user ID'
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        unique=True,
        help_text='Contact phone number (unique)'
    )
    address = models.TextField(
        blank=True,
        null=True,
        help_text='Physical address'
    )
    profile_picture = models.ImageField(
        upload_to=upload_profile_picture,
        blank=True,
        null=True,
        help_text='User profile picture'
    )
    profile_picture_url = models.URLField(
        blank=True,
        null=True,
        help_text='External profile picture URL (e.g., from Google)'
    )
    is_email_verified = models.BooleanField(
        default=False,
        help_text='Whether the user has verified their email via OTP'
    )
    is_profile_complete = models.BooleanField(
        default=False,
        help_text='Whether the user has completed their profile after registration'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def is_admin(self):
        """Check if user has admin role"""
        return self.role == 'admin'

    def is_user(self):
        """Check if user has user role"""
        return self.role == 'user'

    def get_profile_picture_url(self):
        """Get profile picture URL (uploaded file or external URL)"""
        if self.profile_picture:
            return self.profile_picture.url
        elif self.profile_picture_url:
            return self.profile_picture_url
        return None

    def is_google_user(self):
        """Check if user registered via Google"""
        return self.auth_provider == 'google'
