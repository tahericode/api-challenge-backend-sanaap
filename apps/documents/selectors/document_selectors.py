from apps.documents.models.document import Document

def get_user_documents(user):
    return Document.objects.filter(
        uploaded_by=user, is_deleted=False
    ).select_related("uploaded_by").only(
        "id", "original_name", "file_key", "status", "created_at"
    )

def get_document_for_update(doc_id):
    return Document.objects.select_for_update().get(id=doc_id)