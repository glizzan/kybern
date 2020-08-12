from django.contrib.contenttypes.models import ContentType

from concord.actions.client import BaseClient
from concord.communities.client import CommunityClient

from .models import Forum, Post, Group
import groups.state_changes as sc


class GroupClient(CommunityClient):
    community_model = Group

    # state changes

    def change_group_description(self, new_description):
        change = sc.ChangeGroupDescriptionStateChange(new_description=new_description)
        return self.create_and_take_action(change)


class ForumClient(BaseClient):

    # reads

    def get_forum_given_pk(self, pk):
        return Forum.objects.get(pk=pk)

    def get_forums_owned_by_target(self):
        owner = self.target.get_owner()
        ct = ContentType.objects.get_for_model(owner)
        return Forum.objects.filter(owner_object_id=owner.pk, owner_content_type=ct)

    def get_forums_given_owner(self, owner):
        return Forum.objects.filter(owner=owner)   # probably not exactly right

    def get_post_given_pk(self, pk):
        return Post.objects.get(pk=pk)

    def get_posts_for_forum(self):
        return self.target.post_set.all()

    # state change writes

    def create_forum(self, name, description):
        change = sc.AddForumStateChange(name=name, description=description)
        return self.create_and_take_action(change)

    def edit_forum(self, pk, name, description):
        change = sc.EditForumStateChange(pk=pk, name=name, description=description)
        return self.create_and_take_action(change)

    def delete_forum(self, pk):
        change = sc.DeleteForumStateChange(pk=pk)
        return self.create_and_take_action(change)

    def add_post(self, forum_pk, title, content):
        change = sc.AddPostStateChange(forum_pk=forum_pk, title=title, content=content)
        return self.create_and_take_action(change)

    def edit_post(self, pk, title, content):
        change = sc.EditPostStateChange(pk=pk, title=title, content=content)
        return self.create_and_take_action(change)

    def delete_post(self, pk):
        change = sc.DeletePostStateChange(pk=pk)
        return self.create_and_take_action(change)
