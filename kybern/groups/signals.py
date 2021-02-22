from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from concord.utils.helpers import Changes
from concord.permission_resources.utils import set_default_permissions

from .models import Group, Forum


@receiver(post_save, sender=Group)
def retry_action(sender, instance, created, **kwargs):
    """When a new group is created, create a governance forum for it."""
    if created:
        forum = Forum.objects.create(name="Governance Forum", description="Discuss governance", owner=instance,
                                     special="Gov")
        # When a group is created, we know that the sole individual owner of the group is the creator,
        # so we can use that here to add permissions
        actor_pk = instance.roles.get_owners(actors_only=True)[0]
        actor = User.objects.get(pk=actor_pk)
        set_default_permissions(actor, forum)
