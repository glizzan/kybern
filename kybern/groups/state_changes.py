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
        "default_string": "description of group",
        "detail_string": "description of group to {group_description}",
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
        "default_string": "a forum",
        "detail_string": "a forum '{name}'",
        "preposition": "on"
    }

    section = "Forum"
    input_target = Forum   # is this vestigial?
    allowable_targets = ["all_community_models"]
    settable_classes = ["all_community_models", Forum]

    #fields
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
        if not super().validate(actor=actor, target=target):
            return False
        if not self.name and not self.description:
            self.set_validation_error("Must provide either a new name or a new description")
            return False
        return True

    def implement(self, actor, target, action):
        target.name = self.name if self.name else target.name
        target.description = self.description if self.description else target.description
        target.save()
        return target


class DeleteForumStateChange(BaseStateChange):

    descriptive_text = {
        "verb": "delete",
        "default_string": "a forum",
        "preposition": "in"
    }

    section = "Forum"
    allowable_targets = [Forum]
    settable_classes = ["all_community_models", Forum]

    def validate(self, actor, target):
        if not super().validate(actor=actor, target=target):
            return False
        if target.special == "Gov":
            self.set_validation_error(message="You cannot delete a governance forum")
            return False
        return True

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
        "default_string": "a post",
        "detail_string": "a post with title '{title}'"
    }

    section = "Forum"
    input_target = Post
    allowable_targets = [Forum]
    settable_classes = ["all_community_models", Forum]

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
        "default_string": "a post",
        "configurations": [("author_only", "if the user is the post's author")],
        "preposition": "in"
    }

    section = "Forum"
    context_keys = ["forum", "post"]
    allowable_targets = [Post]
    settable_classes = ["all_community_models", Forum, Post]

    title = field_utils.CharField(label="Title")
    content = field_utils.CharField(label="Content")
    author_only = field_utils.BooleanField(label="Only allow author to do this", null_value=False)

    @classmethod
    def get_configurable_fields(cls):
        return {"author_only": {"display": "Only allow author to edit post", "type": "BooleanField"}}

    @classmethod
    def check_configuration_is_valid(cls, configuration):
        """Used primarily when setting permissions, this method checks that the supplied configuration is a valid one.
        By contrast, check_configuration checks a specific action against an already-validated configuration."""
        if "author_only" in configuration and configuration["author_only"] is not None:
            if configuration["author_only"] not in [True, False, "True", "False", "true", "false"]:
                return False, f"author_only must be set to True or False, not {configuration['author_only']}"
        return True, ""

    def check_configuration(self, action, permission):
        configuration = permission.get_configuration()
        if "author_only" in configuration and configuration['author_only']:
            if action.actor.pk != action.target.author.pk:
                return False, "author_only is set to true, so the actor must be the same as the author of the target post"
        return True, None

    def get_context_instances(self, action):
        """Returns the forum and the post object."""
        return {"post": action.target, "forum": action.target.forum}

    def validate(self, actor, target):
        if not super().validate(actor=actor, target=target):
            return False
        if not self.title and not self.content:
            self.set_validation_error("Must provide either a new title or new content when editing post")
            return False
        return True

    def implement(self, actor, target, action):
        target.title = self.title if self.title else target.title
        target.content = self.content if self.content else target.content
        target.save()
        return target


class DeletePostStateChange(BaseStateChange):

    descriptive_text = {
        "verb": "delete",
        "default_string": "a post",
        "configurations": [("author_only", "if the user is the post's author")],
        "preposition": "from"
    }

    section = "Forum"
    context_keys = ["forum", "post"]
    allowable_targets = [Post]
    settable_classes = ["all_community_models", Forum, Post]

    author_only = field_utils.BooleanField(label="Only allow author to do this", null_value=False)

    @classmethod
    def get_configurable_fields(cls):
        return {"author_only": {"display": "Only allow author to edit post", "type": "BooleanField"}}

    @classmethod
    def check_configuration_is_valid(cls, configuration):
        """Used primarily when setting permissions, this method checks that the supplied configuration is a valid one.
        By contrast, check_configuration checks a specific action against an already-validated configuration."""
        if "author_only" in configuration and configuration["author_only"] is not None:
            if configuration["author_only"] not in [True, False, "True", "False", "true", "false"]:
                return False, f"author_only must be set to True or False, not {configuration['author_only']}"
        return True, ""

    def check_configuration(self, action, permission):
        configuration = permission.get_configuration()
        if "author_only" in configuration and configuration['author_only']:
            if action.actor.pk != action.target.author.pk:
                return False, "author_only is true, so the actor must be the same as the author of the target post"
        return True, None

    def get_context_instances(self, action):
        """Returns the forum and the post object."""
        return {"post": action.target, "forum": action.target.forum}

    def implement(self, actor, target, action):
        pk = target.pk
        delete_permissions_on_target(target)
        target.delete()
        return pk
