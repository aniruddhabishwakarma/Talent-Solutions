from django.db import models
from django.conf import settings


class UserSkill(models.Model):
    """Freeform skills entered by users (separate from admin-managed job Skills)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_skills',
    )
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_skills'
        ordering = ['name']
        unique_together = ('user', 'name')

    def __str__(self):
        return self.name
