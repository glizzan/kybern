from concord.actions.state_changes import BaseStateChange
from concord.permission_resources.utils import delete_permissions_on_target

from .models import Group, Forum, Post


###########################
### Group State Changes ###
###########################


class ChangeGroupDescriptionStateChange(BaseStateChange):
    description = "Change group description"
    preposition = "for"
    input_fields = ["group_description"]

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
    input_fields = ["name", "description"]
    input_target = Forum

    def __init__(self, *, name, description):
        self.name = name
        self.description = description

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
    input_fields = ["name", "description"]
    optional_input_fields = ["name", "description"]

    def __init__(self, *, name, description):
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
    input_fields = ["title", "content"]
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
    input_fields = ["title", "content"]
    optional_input_fields = ["title", "content"]

    def __init__(self, *, title, content):
        self.title = title
        self.content = content

    @classmethod
    def get_allowable_targets(cls):
        return [Post]

    @classmethod
    def get_settable_classes(cls):
        return cls.get_community_models() + [Forum, Post]

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

    @classmethod
    def get_allowable_targets(cls):
        return [Post]

    @classmethod
    def get_settable_classes(cls):
        return cls.get_community_models() + [Forum, Post]

    def description_present_tense(self):
        return "remove post"

    def description_past_tense(self):
        return "removed post"

    def implement(self, actor, target):
        pk = target.pk
        delete_permissions_on_target(target)
        target.delete()
        return pk
