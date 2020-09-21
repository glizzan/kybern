from concord.actions.state_changes import BaseStateChange, InputField
from concord.permission_resources.utils import delete_permissions_on_target

from .models import Group, Forum, Post


###########################
### Group State Changes ###
###########################


class ChangeGroupDescriptionStateChange(BaseStateChange):
    description = "Change group description"
    preposition = "for"
    input_fields = [InputField(name="group_description", type="CharField", required=True, validate=True)]

    def __init__(self, group_description):
        self.group_description = group_description

    @classmethod
    def get_allowable_targets(cls):
        return [Group]

    @classmethod
    def get_settable_classes(cls):
        return [Group]

    def description_present_tense(self):
        return f"change description of group to {self.group_description}"

    def description_past_tense(self):
        return f"changed description of group to {self.group_description}"

    def implement(self, actor, target):
        target.group_description = self.group_description
        target.save()
        return target


###########################
### FORUM STATE CHANGES ###
###########################


class AddForumStateChange(BaseStateChange):
    description = "Create a forum"
    preposition = "on"
    input_fields = [InputField(name="name", type="CharField", required=True, validate=True),
                    InputField(name="description", type="CharField", required=False, validate=True)]
    input_target = Forum

    def __init__(self, *, name, description=None):
        self.name = name
        self.description = description if description else ""

    @classmethod
    def get_allowable_targets(cls):
        return cls.get_community_models()

    @classmethod
    def get_settable_classes(cls):
        return cls.get_community_models() + [Forum]

    def description_present_tense(self):
        return f"add forum {self.name}"

    def description_past_tense(self):
        return f"added forum {self.name}"

    def implement(self, actor, target):
        return Forum.objects.create(name=self.name, description=self.description, owner=target.get_owner())


class EditForumStateChange(BaseStateChange):
    description = "Edit a forum"
    preposition = "in"
    input_fields = [InputField(name="name", type="CharField", required=False, validate=True),
                    InputField(name="description", type="CharField", required=False, validate=True)]

    def __init__(self, *, name=None, description=None):
        self.name = name
        self.description = description

    @classmethod
    def get_allowable_targets(cls):
        return [Forum]

    @classmethod
    def get_settable_classes(cls):
        return cls.get_community_models() + [Forum]

    def description_present_tense(self):
        return "edit forum"

    def description_past_tense(self):
        return "edited forum"

    def validate(self, actor, target):
        if not super().validate(actor=actor, target=target):
            return False
        if not self.name and not self.description:
            self.set_validation_error("Must provide either a new name or a new description")
            return False
        return True

    def implement(self, actor, target):
        target.name = self.name if self.name else target.name
        target.description = self.description if self.description else target.description
        target.save()
        return target


class DeleteForumStateChange(BaseStateChange):
    description = "Delete a forum"
    preposition = "in"

    @classmethod
    def get_allowable_targets(cls):
        return [Forum]

    @classmethod
    def get_settable_classes(cls):
        return cls.get_community_models() + [Forum]

    def description_present_tense(self):
        return "remove forum"

    def description_past_tense(self):
        return "removed forum"

    def validate(self, actor, target):
        if not super().validate(actor=actor, target=target):
            return False
        if target.special == "Gov":
            self.set_validation_error(message="You cannot delete a governance forum")
            return False
        return True

    def implement(self, actor, target):
        pk = target.pk
        delete_permissions_on_target(target)
        target.delete()
        return pk


##########################
### Post State Changes ###
##########################


class AddPostStateChange(BaseStateChange):
    description = "Add a post"
    input_fields = [InputField(name="title", type="CharField", required=True, validate=True),
                    InputField(name="content", type="CharField", required=True, validate=True)]
    input_target = Post

    def __init__(self, *, title, content):
        self.title = title
        self.content = content

    @classmethod
    def get_allowable_targets(cls):
        return [Forum]

    @classmethod
    def get_settable_classes(cls):
        return cls.get_community_models() + [Forum]

    def description_present_tense(self):
        return f"add post with title {self.title}"

    def description_past_tense(self):
        return f"added post with title {self.title}"

    def implement(self, actor, target):
        return Post.objects.create(
            title=self.title, content=self.content, author=actor, owner=target.get_owner(), forum=target
        )


class EditPostStateChange(BaseStateChange):
    description = "Edit a post"
    preposition = "in"
    context_keys = ["forum", "post"]
    input_fields = [InputField(name="title", type="CharField", required=False, validate=True),
                    InputField(name="content", type="CharField", required=False, validate=True),
                    InputField(name="author_only", type="BooleanField", required=False, validate=False)]

    def __init__(self, *, title=None, content=None, author_only=False):
        self.title = title
        self.content = content
        self.author_only = author_only

    @classmethod
    def get_allowable_targets(cls):
        return [Post]

    @classmethod
    def get_settable_classes(cls):
        return cls.get_community_models() + [Forum, Post]

    @classmethod
    def get_configurable_fields(cls):
        return {"author_only": {"display": "Only allow author to edit post", "type": "BooleanField"}}

    @classmethod
    def get_configured_field_text(cls, configuration):
        if "author_only" in configuration and configuration['author_only']:
            return ", but only if the user is the post's author"
        return ""

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

    def description_present_tense(self):
        return "edit post"

    def description_past_tense(self):
        return "edited post"

    def validate(self, actor, target):
        if not super().validate(actor=actor, target=target):
            return False
        if not self.title and not self.content:
            self.set_validation_error("Must provide either a new title or new content when editing post")
            return False
        return True

    def implement(self, actor, target):
        target.title = self.title if self.title else target.title
        target.content = self.content if self.content else target.content
        target.save()
        return target


class DeletePostStateChange(BaseStateChange):
    description = "Delete a post"
    preposition = "from"
    context_keys = ["forum", "post"]
    input_fields = [InputField(name="author_only", type="BooleanField", required=False, validate=False)]

    def __init__(self, *, author_only=False):
        self.author_only = author_only

    @classmethod
    def get_allowable_targets(cls):
        return [Post]

    @classmethod
    def get_settable_classes(cls):
        return cls.get_community_models() + [Forum, Post]

    @classmethod
    def get_configurable_fields(cls):
        return {"author_only": {"display": "Only allow author to edit post", "type": "BooleanField"}}

    @classmethod
    def get_configured_field_text(cls, configuration):
        if "author_only" in configuration and configuration['author_only']:
            return ", but only if the user is the post's author"
        return ""

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

    def description_present_tense(self):
        return "remove post"

    def description_past_tense(self):
        return "removed post"

    def implement(self, actor, target):
        pk = target.pk
        delete_permissions_on_target(target)
        target.delete()
        return pk
