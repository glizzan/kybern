"""Management command which sends daily notifications."""

from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.core.mail import send_mail



class Command(BaseCommand):
    help = 'Sends notifications as daily email.'

    def handle(self, *args, **options):

        from accounts.models import Notification

        user_notify_map = {}

        # create map of unsent notifications
        for notification in Notification.objects.filter(email_type="day"):
            if not notification.sent:
                if notification.user not in user_notify_map:
                    user_notify_map[notification.user] = []
                user_notify_map[notification.user].append(notification)

        for user, notifications in user_notify_map.items():

            if notifications:

                ctx = {"user": user}
                ctx["approval_notifications"] = [n for n in notifications if n.notes == "approval"]
                ctx["creator_notifications"] = [n for n in notifications if n.notes == "creator"]
                ctx["other_notifications"] = [n for n in notifications if n.notes == "everything"]
                ctx["resolved_notifications"] = [n for n in notifications if n.notes == "resolved"]

                msg = render_to_string('emails/daily_notification_summary.txt', ctx)
                send_mail("Notification from Kybern", msg, None, [user.email], fail_silently=False)

                for notification in notifications:
                    notification.sent = True
                    notification.save()
