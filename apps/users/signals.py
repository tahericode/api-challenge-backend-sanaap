from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def create_roles(sender, **kwargs):
    for role in ["admin", "editor", "viewer"]:
        Group.objects.get_or_create(name=role)