from django.core.files.storage import default_storage
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.documents.models import Document
from apps.documents.services.document_service import create_document
from apps.documents.api.permissions import DocumentRBACPermission
from core.commons.pagination.custom_pagination import DocumentPagination
from .serializers import DocumentSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    """
    Document API with RBAC, filtering, pagination, background processing,
    and secure download endpoint.
    """

    queryset = Document.objects.filter(is_deleted=False)
    serializer_class = DocumentSerializer
    permission_classes = [DocumentRBACPermission]
    pagination_class = DocumentPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ["uploaded_by", "status"]
    search_fields = ["original_name"]
    ordering_fields = ["created_at", "size"]

    def create(self, request, *args, **kwargs):
        """
        Handle file upload and delegate document creation to service layer.
        """
        upload = request.FILES.get("file")
        if not upload:
            return Response(
                {"detail": "Missing file"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        idem_key = request.headers.get("Idempotency-Key")
        if not idem_key:
            return Response(
                {"detail": "Missing Idempotency-Key header"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Store file using configured MinIO-backed storage
        file_key = default_storage.save(upload.name, upload)

        doc = create_document(
            user=request.user,
            file_key=file_key,
            original_name=upload.name,
            mime_type=upload.content_type,
            size=upload.size,
            idem_key=idem_key,
        )

        serializer = self.get_serializer(doc)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        """
        Secure download URL endpoint.
        Returns an authenticated URL to access the file via storage backend.
        """
        document = self.get_object()
        url = default_storage.url(document.file_key)
        return Response({"url": url})
