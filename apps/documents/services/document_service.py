from django.db import transaction
from django.db.models import F
from apps.documents.models.document import Document
from apps.documents.models.idempotency import IdempotencyKey
from apps.documents.tasks import process_document

class IdempotencyError(Exception):
    pass

@transaction.atomic
def create_document(user, file_key, original_name, mime_type, size, idem_key: str):
    if IdempotencyKey.objects.filter(key=idem_key).exists():
        raise IdempotencyError(f"Idempotency key {idem_key} already used.")

    IdempotencyKey.objects.create(key=idem_key)

    doc = Document.objects.create(
        uploaded_by=user,
        file_key=file_key,
        original_name=original_name,
        mime_type=mime_type,
        size=size,
    )

    # Best-effort background processing: do not fail the API
    # if the Celery broker/worker is unavailable.
    try:
        process_document.delay(doc.id)
    except Exception:
        # In a real system we would log this properly (e.g. sentry/logger).
        pass

    return doc


@transaction.atomic
def update_document(doc_id, data, client_version):
    # optimistic concurrency
    updated = Document.objects.filter(
        id=doc_id,
        version=client_version
    ).update(
        title=data.get("title"),
        version=F("version") + 1
    )

    if not updated:
        raise Exception("ConflictError: document version mismatch")