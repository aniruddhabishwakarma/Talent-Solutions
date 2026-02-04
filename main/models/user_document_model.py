from django.db import models
from django.conf import settings
import os
import uuid


def upload_document_passport(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    unique = uuid.uuid4().hex[:8]
    return f"documents/passport_photos/{instance.user.id}_passport_{unique}{ext}"


def upload_document_cv(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    unique = uuid.uuid4().hex[:8]
    return f"documents/cvs/{instance.user.id}_cv_{unique}{ext}"


class UserDocument(models.Model):
    """Stores user documents like passport and CV."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='documents'
    )

    # Passport
    passport_number = models.CharField(max_length=50, blank=True, null=True)
    passport_photo = models.ImageField(upload_to=upload_document_passport, blank=True, null=True)

    # CV
    cv = models.FileField(upload_to=upload_document_cv, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_documents'

    def __str__(self):
        return f"Documents - {self.user.username}"
