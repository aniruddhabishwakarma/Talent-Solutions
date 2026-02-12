from django.db import models
from django.utils import timezone


class ContactMessage(models.Model):
    """
    Model to store contact form submissions from website visitors
    """
    # Sender Information
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=300)
    message = models.TextField()

    # Metadata
    submitted_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    replied_at = models.DateTimeField(blank=True, null=True)

    # Admin notes
    admin_notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"{self.full_name} - {self.subject[:50]}"

    def mark_as_read(self):
        """Mark the message as read"""
        self.is_read = True
        self.save()

    def mark_as_replied(self):
        """Mark the message as replied"""
        self.replied_at = timezone.now()
        self.save()
