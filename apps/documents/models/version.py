import uuid
from django.db import models
from .document import Document

class DocumentVersion(models.Model):

    id=models.UUIDField(primary_key=True,default=uuid.uuid4)

    document=models.ForeignKey(
        Document,
        related_name="versions",
        on_delete=models.CASCADE
    )

    file_key=models.CharField(max_length=500)

    created_at=models.DateTimeField(auto_now_add=True)