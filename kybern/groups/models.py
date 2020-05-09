import importlib, inspect

from django.db import models
from django.utils import timezone

from concord.communities.models import BaseCommunityModel
from concord.actions.models import PermissionedModel

from accounts.models import User


class Group(BaseCommunityModel):
    group_description = models.CharField(max_length=500)

    @classmethod
    def get_state_change_objects(cls):
        """Workaround for get_settable_permissions.  Definitely doesn't belong here
        but not sure where it actually goes yet."""
        # NOTE: difference between here and concord is we don't need the relative path
        # plus project name -- just the app label.
        relative_import = cls._meta.app_label + ".state_changes"
        state_changes_module = importlib.import_module(relative_import)
        return inspect.getmembers(state_changes_module) 


class Forum(PermissionedModel):
    name = models.CharField(max_length=120)
    description = models.CharField(max_length=500)

    # note that there's no direct relationship to a group here, instead this is handled by the owner field

    @classmethod
    def get_state_change_objects(cls):
        """Workaround for get_settable_permissions.  Definitely doesn't belong here
        but not sure where it actually goes yet."""
        # NOTE: difference between here and concord is we don't need the relative path
        # plus project name -- just the app label.
        relative_import = cls._meta.app_label + ".state_changes"
        state_changes_module = importlib.import_module(relative_import)
        return inspect.getmembers(state_changes_module) 

    def get_name(self):
        return self.name

    def get_nested_objects(self):
        return [self.get_owner()]


class Post(PermissionedModel):
    title = models.CharField(max_length=120)
    content = models.CharField(max_length=500)
    created = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)   # TODO: reconsider the on_delete
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE)   # TODO: reconsider the on_delete

    def get_name(self):
        return self.title

    def get_nested_objects(self):
        return [self.get_owner(), self.forum]


