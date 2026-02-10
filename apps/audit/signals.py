from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.audit.models import AuditLog

def log_change(user, action, instance, changes=None):
    AuditLog.objects.create(
        user=user,
        action=action,
        model_name=instance.__class__.__name__,
        object_id=str(instance.pk),
        changes=changes
    )

# example for documents
from apps.documents.models.document import Document

@receiver(post_save, sender=Document)
def audit_document_save(sender, instance, created, **kwargs):
    action = "create" if created else "update"
    log_change(user=getattr(instance, "uploaded_by", None), action=action, instance=instance)

@receiver(post_delete, sender=Document)
def audit_document_delete(sender, instance, **kwargs):
    log_change(user=getattr(instance, "uploaded_by", None), action="delete", instance=instance)