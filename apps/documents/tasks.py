from celery import shared_task

@shared_task
def process_document(document_id):
    print(f"Processing document {document_id} in background...")