from django.apps import AppConfig


class AuditConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.audit"

    def ready(self):
        # Import signal handlers so that audit logging is active
        from . import signals  # noqa: F401

