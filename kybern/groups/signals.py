from django.db.models.signals import post_save
from django.dispatch import receiver

from concord.actions.utils import Changes

from .models import Group, Forum


@receiver(post_save, sender=Group)
def retry_action(sender, instance, created, **kwargs):
    """When a new group is created, create a governance forum for it."""
    if created:
        name = "Governance Forum"
        description = f"Discuss governance"
        Forum.objects.create(name=name, description=description, owner=instance, special="Gov")
