from django.core.exceptions import ValidationError

from concord.actions.state_changes import BaseStateChange
from concord.permission_resources.utils import delete_permissions_on_target
from concord.utils import field_utils

from .models import Group, Forum, Post


###########################
### Group State Changes ###
###########################


class ChangeGroupDescriptionStateChange(BaseStateChange):

    descriptive_text = {
        "verb": "change",
        "default_string": "group description",
        "detail_string": "group description to {group_description}",
        "preposition": "for"
    }

    section = "Community"
    allowable_targets = [Group]

    group_description = field_utils.CharField(label="Group description", required=True)

    def implement(self, actor, target, action):
        target.group_description = self.group_description
        target.save()
        return target


###########################
### FORUM STATE CHANGES ###
###########################


class AddForumStateChange(BaseStateChange):

    descriptive_text = {
        "verb": "add",
        "default_string": "forum",
        "detail_string": "forum '{name}'",
        "preposition": "on"
    }

    section = "Forum"
    input_target = Forum   # is this vestigial?
    allowable_targets = ["all_community_models"]
    settable_classes = ["all_community_models", Forum]

    # Fields
    name = field_utils.CharField(label="Name of forum", required=True)
    description = field_utils.CharField(label="Forum description", null_value="")

    def implement(self, actor, target, action):
        forum = Forum.objects.create(name=self.name, description=self.description, owner=target.get_owner())
        self.set_default_permissions(actor, forum)
        return forum


class EditForumStateChange(BaseStateChange):

    descriptive_text = {
        "verb": "edit",
        "default_string": "forum",
        "preposition": "in"
    }

    section = "Forum"
    allowable_targets = [Forum]
    settable_classes = ["all_community_models", Forum]

    name = field_utils.CharField(label="Name of forum")
    description = field_utils.CharField(label="Forum description")

    def validate(self, actor, target):
        if not self.name and not self.description:
            raise ValidationError("Must provide either a new name or a new description")

    def implement(self, actor, target, action):
        target.name = self.name if self.name else target.name
        target.description = self.description if self.description else target.description
        target.save()
        return target


class DeleteForumStateChange(BaseStateChange):

    descriptive_text = {
        "verb": "delete",
        "default_string": "forum",
        "preposition": "in"
    }

    section = "Forum"
    allowable_targets = [Forum]
    settable_classes = ["all_community_models", Forum]

    def validate(self, actor, target):
        if target.special == "Gov":
            raise ValidationError("You cannot delete a governance forum")

    def implement(self, actor, target, action):
        pk = target.pk
        delete_permissions_on_target(target)
        target.delete()
        return pk


##########################
### Post State Changes ###
##########################


class AddPostStateChange(BaseStateChange):

    descriptive_text = {
        "verb": "add",
        "default_string": "post",
        "detail_string": "post with title '{title}'"
    }

    section = "Forum"
    input_target = Post
    allowable_targets = [Forum]
    settable_classes = ["all_community_models", Forum]
    model_based_validation = (Post, ["title", "content"])

    # Fields
    title = field_utils.CharField(label="Title", required=True)
    content = field_utils.CharField(label="Content", required=True)

    def implement(self, actor, target, action):
        post = Post.objects.create(
            title=self.title, content=self.content, author=actor, owner=target.get_owner(), forum=target
        )
        self.set_default_permissions(actor, post)
        return post


class EditPostStateChange(BaseStateChange):

    descriptive_text = {
        "verb": "edit",
        "default_string": "post",
        "preposition": "in"
    }

    section = "Forum"
    context_keys = ["forum", "post"]
    allowable_targets = [Post]
    settable_classes = ["all_community_models", Forum, Post]
    linked_filters = ["CreatorOnly"]
    model_based_validation = (Post, ["title", "content"])

    title = field_utils.CharField(label="Title")
    content = field_utils.CharField(label="Content")

    def get_context_instances(self, action):
        """Returns the forum and the post object."""
        return {"post": action.target, "forum": action.target.forum}

    def validate(self, actor, target):
        if not self.title and not self.content:
            raise ValidationError("Must provide either a new title or new content when editing post")

    def implement(self, actor, target, action):
        target.title = self.title if self.title else target.title
        target.content = self.content if self.content else target.content
        target.save()
        return target


class DeletePostStateChange(BaseStateChange):

    descriptive_text = {
        "verb": "delete",
        "default_string": "post",
        "preposition": "from"
    }

    section = "Forum"
    context_keys = ["forum", "post"]
    allowable_targets = [Post]
    settable_classes = ["all_community_models", Forum, Post]
    linked_filters = ["CreatorOnly"]

    def get_context_instances(self, action):
        """Returns the forum and the post object."""
        return {"post": action.target, "forum": action.target.forum}

    def implement(self, actor, target, action):
        pk = target.pk
        delete_permissions_on_target(target)
        target.delete()
        return pk
