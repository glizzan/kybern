from concord.actions.state_changes import BaseStateChange

from .models import Group


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