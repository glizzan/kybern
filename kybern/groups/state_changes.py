from concord.actions.state_changes import BaseStateChange

from .models import Group, Forum


###########################
### Group State Changes ###
###########################


class ChangeGroupDescriptionChange(BaseStateChange):
    description = "Change group description"

    def __init__(self, new_description):
        self.new_description = new_description

    @classmethod
    def get_allowable_targets(cls):
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


class AddForumChange(BaseStateChange):
    description = "Create a forum"

    def __init__(self, *, name, description):
        self.name = name
        self.description = description

    @classmethod
    def get_allowable_targets(cls):
        return cls.get_community_models()

    def description_present_tense(self):
        return "add forum %s" % self.name  

    def description_past_tense(self):
        return "added forum %s" % self.name

    def validate(self, actor, target):
        return True
        
    def implement(self, actor, target):
        return Forum.objects.create(name=self.name, description=self.description, owner=target.get_owner())

     
class DeleteForumChange(BaseStateChange):
    description = "Delete a forum"

    def __init__(self, *, pk):
        self.pk = pk

    @classmethod
    def get_allowable_targets(cls):
        return cls.get_community_models()

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


class EditForumChange(BaseStateChange):
    description = "Edit a forum"
    preposition = "on"

    def __init__(self, *, pk, name, description):
        self.pk = pk
        self.name = name
        self.description = description

    @classmethod
    def get_allowable_targets(cls):
        return cls.get_community_models()

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


# #############
# ### LATER ###
# #############

# class AddPostToForumChange(BaseStateChange):
#     ... # Target is forum

# class EditForumPostChange(BaseStateChange):
#     ... # Targets are either post OR forum

# class DeleteForumPostChange(BaseStateChange):
#     ... # Targets are either post OR forum