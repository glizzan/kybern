from django.views import generic
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from concord.communities.client import CommunityClient
from accounts.models import Profile
from groups.models import Group


# FIXME: this probably doesn't belong here
class GroupClient(CommunityClient):
    """Easy way to replace the default community model with the one we want to use here, group."""
    community_model = Group


class IndexView(generic.TemplateView):
    template_name = 'accounts/index.html'


class ProfileView(generic.DetailView):
    model = Profile
    template_name = 'accounts/profile.html'

    def get_object(self):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # FIXME: this seems deeply inefficient given what's involved on the backend 
        groupClient = GroupClient(actor=self.request.user)
        leader_list, member_list = groupClient.get_communities_for_user(user_pk=self.request.user.pk, split=True)
        context["leadership_groups"] = leader_list
        context["other_groups"] = member_list
        return context
