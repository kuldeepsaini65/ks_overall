from django.db import models
from django.contrib.auth.models import User


class LogFolder(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='%(class)s_created'
    )

    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='%(class)s_updated'
    )

    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True




