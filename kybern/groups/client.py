from django.contrib.contenttypes.models import ContentType

from concord.actions.client import BaseClient
from concord.communities.client import CommunityClient

from .models import Forum, Post, Group
import groups.state_changes as sc


class GroupClient(CommunityClient):
    community_model = Group
    app_name = "groups"

    # state changes

    # def change_group_description(self, new_description):
    #     change = sc.ChangeGroupDescriptionStateChange(group_description=new_description)
    #     return self.create_and_take_action(change)


class ForumClient(BaseClient):
    app_name = "groups"

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

    # def add_forum(self, name, description):
    #     change = sc.AddForumStateChange(name=name, description=description)
    #     return self.create_and_take_action(change)

    # def edit_forum(self, name, description):
    #     change = sc.EditForumStateChange(name=name, description=description)
    #     return self.create_and_take_action(change)

    # def delete_forum(self):
    #     change = sc.DeleteForumStateChange()
    #     return self.create_and_take_action(change)

    # def add_post(self, title, content):
    #     change = sc.AddPostStateChange(title=title, content=content)
    #     return self.create_and_take_action(change)

    # def edit_post(self, title, content):
    #     change = sc.EditPostStateChange(title=title, content=content)
    #     return self.create_and_take_action(change)

    # def delete_post(self):
    #     change = sc.DeletePostStateChange()
    #     return self.create_and_take_action(change)
