from django.contrib.contenttypes.models import ContentType

from concord.actions.client import BaseClient

from .models import Forum
from .state_changes import AddForumChange, DeleteForumChange, EditForumChange


class ForumClient(BaseClient):

    # FIXME: right now forum target is owner, but we probably want to make the forum itself the target, no?

    # reads

    def get_forum_given_pk(self, pk):
        return Forum.objects.get(pk=pk)

    def get_forums_owned_by_target(self):
        owner = self.target.get_owner()
        ct = ContentType.objects.get_for_model(owner)
        return Forum.objects.filter(owner_object_id=owner.pk, owner_content_type=ct)

    def get_forums_given_owner(self, owner):
        return Forum.objects.filter(owner=owner)   # probably not exactly right

    # state change writes

    def create_forum(self, name, description):
        change = AddForumChange(name=name, description=description)
        return self.create_and_take_action(change)

    def edit_forum(self, pk, name, description):
        change = EditForumChange(pk=pk, name=name, description=description)
        return self.create_and_take_action(change)

    def delete_forum(self, pk):
        change = DeleteForumChange(pk=pk)
        return self.create_and_take_action(change)
