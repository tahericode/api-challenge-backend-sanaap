import uuid
from django.db import models

class IdempotencyKey(models.Model):
    key = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_object_id = models.UUIDField(null=True, blank=True)

    def __str__(self):
        return self.key