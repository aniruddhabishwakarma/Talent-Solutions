from django.db import models
from django.conf import settings
import os
import uuid
import time


def upload_application_passport(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    user_id = instance.user.id if instance.user else 'guest'
    unique = uuid.uuid4().hex[:8]
    return f"applications/passport_photos/{user_id}_passport_{unique}{ext}"


def upload_application_cv(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    user_id = instance.user.id if instance.user else 'guest'
    unique = uuid.uuid4().hex[:8]
    return f"applications/cvs/{user_id}_cv_{unique}{ext}"


APPLICATION_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('reviewed', 'Under Review'),
    ('shortlisted', 'Shortlisted'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
]


class JobApplication(models.Model):
    """Model for job applications."""

    # Related Job
    job = models.ForeignKey(
        'Job',
        on_delete=models.CASCADE,
        related_name='applications'
    )

    # Applicant (optional - for logged in users)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='job_applications'
    )

    # Required Fields
    full_name = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=20)
    passport_number = models.CharField(max_length=50)
    passport_photo = models.ImageField(upload_to=upload_application_passport)

    # Skills
    skills = models.ManyToManyField('Skill', related_name='applications')

    # Optional Fields
    cv = models.FileField(upload_to=upload_application_cv, blank=True, null=True)

    # Application Status
    status = models.CharField(
        max_length=20,
        choices=APPLICATION_STATUS_CHOICES,
        default='pending'
    )

    # Admin notes (internal use)
    admin_notes = models.TextField(blank=True, null=True)

    # Rejection reason (sent to applicant via email later)
    rejection_reason = models.TextField(blank=True, null=True)

    # Timestamps (epoch milliseconds)
    created_at = models.BigIntegerField(editable=False)
    updated_at = models.BigIntegerField(editable=False)

    class Meta:
        db_table = 'job_applications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.job.title}"

    def save(self, *args, **kwargs):
        # Set created_at on first save (epoch milliseconds)
        if not self.created_at:
            self.created_at = int(time.time() * 1000)

        # Always update updated_at (epoch milliseconds)
        self.updated_at = int(time.time() * 1000)

        super().save(*args, **kwargs)

    @property
    def created_at_datetime(self):
        """Convert epoch milliseconds to datetime."""
        from datetime import datetime
        return datetime.fromtimestamp(self.created_at / 1000)

    @property
    def updated_at_datetime(self):
        """Convert epoch milliseconds to datetime."""
        from datetime import datetime
        return datetime.fromtimestamp(self.updated_at / 1000)

    def get_status_color(self):
        """Get Bootstrap/Tailwind color class for status."""
        colors = {
            'pending': 'yellow',
            'reviewed': 'blue',
            'shortlisted': 'purple',
            'accepted': 'green',
            'rejected': 'red',
        }
        return colors.get(self.status, 'gray')
