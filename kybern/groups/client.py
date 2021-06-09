from django.contrib.contenttypes.models import ContentType

from concord.actions.client import BaseClient
from concord.communities.client import CommunityClient

from .models import Forum, Post, Group
import groups.state_changes as sc


class GroupClient(CommunityClient):
    community_model = Group
    app_name = "groups"


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
