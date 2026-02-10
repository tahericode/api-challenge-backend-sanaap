from django.contrib import admin

from apps.documents.models import Document
from apps.documents.models.idempotency import IdempotencyKey
from apps.documents.models.version import DocumentVersion


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "original_name", "uploaded_by", "status", "created_at")
    list_filter = ("status", "uploaded_by")
    search_fields = ("original_name", "file_key")


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ("id", "document", "file_key", "created_at")


@admin.register(IdempotencyKey)
class IdempotencyKeyAdmin(admin.ModelAdmin):
    list_display = ("key", "created_at", "processed_object_id")
