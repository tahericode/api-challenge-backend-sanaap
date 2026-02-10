import uuid
from django.db import models
from django.conf import settings


class Document(models.Model):

    class Status(models.TextChoices):
        UPLOADING="uploading"
        READY="ready"
        FAILED="failed"

    id=models.UUIDField(primary_key=True,default=uuid.uuid4)

    file_key=models.CharField(max_length=500,unique=True)

    original_name=models.CharField(max_length=255)

    mime_type=models.CharField(max_length=100)

    size=models.BigIntegerField()

    status=models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UPLOADING
    )

    uploaded_by=models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    created_at=models.DateTimeField(auto_now_add=True)

    is_deleted=models.BooleanField(default=False)

    class Meta:
        indexes=[
            models.Index(fields=["uploaded_by"]),
            models.Index(fields=["created_at"]),
        ]