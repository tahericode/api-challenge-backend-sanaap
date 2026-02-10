from rest_framework import serializers

from apps.documents.models import Document


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            "id",
            "file_key",
            "original_name",
            "mime_type",
            "size",
            "status",
            "uploaded_by",
            "created_at",
        ]

