from concord.actions.state_changes import BaseStateChange

from .models import Group, Forum, Post


###########################
### Group State Changes ###
###########################


class ChangeGroupDescriptionStateChange(BaseStateChange):
    description = "Change group description"
    preposition = "for"

    def __init__(self, new_description):
        self.new_description = new_description

    @classmethod
    def get_allowable_targets(cls):
        return [Group]

    @classmethod
    def get_settable_classes(cls):
        return [Group]

    def description_present_tense(self):
        return "change description of group to %s" % (self.new_description)  

    def description_past_tense(self):
        return "changed description of group to %s" % (self.new_description)  

    def validate(self, actor, target):
        """
        TODO: put real logic here
        """
        if actor and target and self.new_description:
            return True
        return False

    def implement(self, actor, target):
        target.group_description = self.new_description
        target.save()
        return target


###########################
### FORUM STATE CHANGES ###
###########################


class AddForumStateChange(BaseStateChange):
    description = "Create a forum"
    preposition = "on"

    def __init__(self, *, name, description):
        self.name = name
        self.description = description

    @classmethod
    def get_allowable_targets(cls):
        return cls.get_community_models()

    @classmethod
    def get_settable_classes(cls):
        return cls.get_community_models()

    def description_present_tense(self):
        return "add forum %s" % self.name  

    def description_past_tense(self):
        return "added forum %s" % self.name

    def validate(self, actor, target):
        return True

    def implement(self, actor, target):
        return Forum.objects.create(name=self.name, description=self.description, owner=target.get_owner())


class DeleteForumStateChange(BaseStateChange):
    description = "Delete a forum"
    preposition = "in"

    def __init__(self, *, pk):
        self.pk = pk

    @classmethod
    def get_allowable_targets(cls):
        return [Forum]

    @classmethod
    def get_settable_classes(cls):
        return cls.get_community_models() + [Forum]

    def description_present_tense(self):
        return "remove forum %s" % str(self.pk)  

    def description_past_tense(self):
        return "removed forum %s" % str(self.pk)

    def validate(self, actor, target):
        return True

    def implement(self, actor, target):
        forum = Forum.objects.get(pk=self.pk)
        forum.delete()
        return self.pk


class EditForumStateChange(BaseStateChange):
    description = "Edit a forum"
    preposition = "in"

    def __init__(self, *, pk, name, description):
        self.pk = pk
        self.name = name
        self.description = description

    @classmethod
    def get_allowable_targets(cls):
        return [Forum]

    @classmethod
    def get_settable_classes(cls):
        return cls.get_community_models() + [Forum]

    def description_present_tense(self):
        return "edit forum %s" % str(self.pk)    

    def description_past_tense(self):
        return "edited forum %s" % str(self.pk) 

    def validate(self, actor, target):
        if not self.name and not self.description:
            self.set_validation_error("Must provide either a new name or a new description")
            return False
        return True

    def implement(self, actor, target):
        forum = Forum.objects.get(pk=self.pk)
        if self.name:
            forum.name = self.name
        if self.description:
            forum.description = self.description
        forum.save()
        return forum


##########################
### Post State Changes ###
##########################


class AddPostStateChange(BaseStateChange):
    description = "Add a post"

    def __init__(self, *, forum_pk, title, content):
        self.forum_pk = forum_pk
        self.title = title
        self.content = content

    @classmethod
    def get_allowable_targets(cls):
        return [Forum]

    @classmethod
    def get_settable_classes(cls):
        return cls.get_community_models() + [Forum]

    def description_present_tense(self):
        return "add post with title %s" % str(self.title)    

    def description_past_tense(self):
        return "added post with title %s" % str(self.title) 

    def validate(self, actor, target):
        if not self.forum_pk:
            self.set_validation_error("Must specify forum for post")
            return False
        if not self.title:
            self.set_validation_error("Must provide a title for your post")
            return False
        return True

    def implement(self, actor, target):
        forum = Forum.objects.get(pk=self.forum_pk)
        return Post.objects.create(
            title=self.title, content=self.content, author=actor, owner=target.get_owner(), forum=forum
        )


class EditPostStateChange(BaseStateChange):
    description = "Edit a post"
    preposition = "in"

    def __init__(self, *, pk, title, content):
        self.pk = pk
        self.title = title
        self.content = content

    @classmethod
    def get_allowable_targets(cls):
        return [Post]

    @classmethod
    def get_settable_classes(cls):
        return cls.get_community_models() + [Forum, Post]

    def description_present_tense(self):
        return "edit post %s" % str(self.pk)    

    def description_past_tense(self):
        return "edited post %s" % str(self.pk) 

    def validate(self, actor, target):
        if not self.pk:
            self.set_validation_error("Must specify post to edit")
            return False
        if not self.title and not self.content:
            self.set_validation_error("Must provide either a new title or new content when editing post")
            return False
        return True

    def implement(self, actor, target):
        post = Post.objects.get(pk=self.pk)
        if self.title:
            post.title = self.title
        if self.content:
            post.content = self.content
        post.save()
        return post


class DeletePostStateChange(BaseStateChange):
    description = "Delete a post"
    preposition = "from"

    def __init__(self, *, pk):
        self.pk = pk

    @classmethod
    def get_allowable_targets(cls):
        return [Post]

    @classmethod
    def get_settable_classes(cls):
        return cls.get_community_models() + [Forum, Post]

    def description_present_tense(self):
        return "remove post %s" % str(self.pk)  

    def description_past_tense(self):
        return "removed post %s" % str(self.pk)

    def validate(self, actor, target):
        if not self.pk:
            self.set_validation_error("Must provide pk of post to be deleted")
            return False
        return True

    def implement(self, actor, target):
        post = Post.objects.get(pk=self.pk)
        post.delete()
        return self.pk
