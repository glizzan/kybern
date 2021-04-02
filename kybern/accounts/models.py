from django.db import models
from django.contrib.auth.models import User as DjangoUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.urls import reverse
from django.template.loader import render_to_string

from django_q.tasks import async_task
from django_q.tasks import schedule

from concord.actions.models import Action


class ActiveUsersManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class User(DjangoUser):
    """Extends django's inbuilt user model to get only active users when calling User.objects.all()"""

    objects = ActiveUsersManager()

    class Meta:
        proxy = True


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)


@receiver(post_save, sender=DjangoUser)
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()


class NotificationsSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notify_settings')
    EMAIL_CHOICES = [
        ('now', 'Immediately'),
        ('day', 'Daily'),
        ('nev', 'Never'),
    ]
    send_emails = models.CharField(max_length=3, choices=EMAIL_CHOICES, default='now')
    always_notify_everything = models.BooleanField(default=False)
    always_notify_approval = models.BooleanField(default=True)
    always_notify_creator = models.BooleanField(default=True)
    always_notify_action_resolved = models.BooleanField(default=True)


@receiver(post_save, sender=DjangoUser)
@receiver(post_save, sender=User)
def create_notifications_settings(sender, instance, created, **kwargs):
    if created:
        NotificationsSettings.objects.create(user=instance)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    sent = models.BooleanField(default=False)
    EMAIL_CHOICES = [
        ('now', 'Immediately'),
        ('day', 'Daily'),
        ('nev', 'Never'),
    ]
    email_type = models.CharField(max_length=3, choices=EMAIL_CHOICES, default='nev')
    notes = models.CharField(max_length=100, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification @ {self.created} for {self.user} about [{self.action}] ({self.email_type}, {self.sent}, {self.notes})"


@receiver(post_save, sender=Action)
def create_or_update_notification(sender, instance, created, **kwargs):
    """For now, we only notify on action creation, but we probably want to notify on update eventually."""

    from mysite.settings import TESTING
    if TESTING:
        return

    if created:
        async_task('accounts.tasks.generate_notifications', instance)
    else:
        async_task('accounts.tasks.create_resolved_notification', instance)


def send_notification_email(notification):
    msg = render_to_string('emails/immediate_notifications.html', {"notification": notification})
    send_mail("Notification from Kybern", msg, None, [notification.user.email], fail_silently=False, html_message=msg)
    notification.sent = True
    notification.save()


@receiver(post_save, sender=Notification)
def trigger_immediate_email(sender, instance, created, **kwargs):
    if not instance.sent and instance.email_type == "now":
        send_notification_email(instance)
