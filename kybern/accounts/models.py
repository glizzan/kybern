from django.db import models
from django.contrib.auth.models import User as DjangoUser
from django.db.models.signals import post_save
from django.dispatch import receiver


class ActiveUsersManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class User(User):
    """Extends django's inbuilt user model to get only active users when calling User.objects.all()"""

    objects = ActiveUsersManager()

    class Meta:
        proxy = True
    


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)


@receiver(post_save, sender=DjangoUser)
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=DjangoUser)
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()