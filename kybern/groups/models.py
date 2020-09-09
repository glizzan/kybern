import importlib, inspect

from django.db import models
from django.utils import timezone

from concord.communities.models import BaseCommunityModel
from concord.actions.models import PermissionedModel

from accounts.models import User


class Group(BaseCommunityModel):
    group_description = models.CharField(max_length=500)


class Forum(PermissionedModel):
    name = models.CharField(max_length=120)
    description = models.CharField(max_length=500)
    SPECIAL_FORUM_CHOICES = (
        ('None', 'None'),
        ('Gov', 'Governance Forum'),
    )
    special = models.CharField(max_length=4, choices=SPECIAL_FORUM_CHOICES, default="None")

    def get_name(self):
        return self.name

    def get_nested_objects(self):
        return [self.get_owner()]


class Post(PermissionedModel):
    title = models.CharField(max_length=120)
    content = models.CharField(max_length=500)
    created = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)   
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE)

    def get_name(self):
        return self.title

    def get_nested_objects(self):
        return [self.get_owner(), self.forum]
