import time

from django.contrib.auth.models import User

from concord.utils.helpers import Client
from .models import Notification


def user_approval_match(user, action):
    """Checks if the given action has triggered a decision-making condition and, if so, checks whether the
    given user is eligible to participate in that decision."""

    time.sleep(5)  # give action time to go through pipeline & create conditions

    for condition in Client().Conditional.get_condition_items_for_action(action_pk=action.pk):
        permissions = Client().PermissionResource.get_permissions_on_object(target_object=condition)
        for permission in permissions:
            match = Client().PermissionResource.actor_satisfies_permission(actor=user, permission=permission)
            if match:
                return True

    return False


def generate_notifications(action):

    for member_pk in action.target.get_owner().roles.get_members(): # get members of community owner of target

        user = User.objects.get(pk=member_pk)

        if action.actor == user:
            continue  # no notifications when user took the action

        if user.notify_settings.always_notify_everything:
            note = "everything"
        elif user.notify_settings.always_notify_creator and action.target.creator == user:
            note = "creator"
        elif user.notify_settings.always_notify_approval and user_approval_match(user, action):
            note = "approval"
        else:
            note = None

        if note:
            notification = Notification(user=user, action=action, sent=False, notes=note,
                email_type=user.notify_settings.send_emails)
            notification.save()
        else:
            print("No matches, sorry")


def create_resolved_notification(action):

    if action.is_resolved:

        notification = Notification(user=action.actor, action=action, sent=False, notes="resolved",
                                    email_type=action.actor.notify_settings.send_emails)
        notification.save()
