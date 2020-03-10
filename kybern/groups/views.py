from django.views import generic
from django.http import HttpResponseRedirect, JsonResponse

from django.urls import reverse

from concord.actions.client import ActionClient
from concord.communities.client import CommunityClient

from .models import Group


class GroupListView(generic.ListView):
    model = Group
    template_name = 'groups/group_list.html'


class GroupDetailView(generic.DetailView):
    model = Group
    template_name = 'groups/group_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        actionClient = ActionClient(actor=self.request.user, 
            target=self.object)
        context['actions'] = actionClient.get_action_history_given_target()
        communityClient = CommunityClient(actor=self.request.user, 
            target=self.object)
        context['roles'] = communityClient.get_role_names()
        return context

class GroupCreateView(generic.edit.CreateView):
    model = Group
    template_name = 'groups/group_create.html'
    fields = ['name', 'group_description', 'governing_permission_enabled',
        'foundational_permission_enabled']

    def form_valid(self, form):
        # FIXME: should this be so fiddly?
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.roles.initialize_with_creator(creator=self.request.user.pk)
        self.object.save()
        return HttpResponseRedirect(reverse('group_detail', kwargs={'pk': self.object.pk}))


# helper methods, likely to be moved to concord

def add_role(request, target, role_name):
    communityClient = CommunityClient(actor=request.user)
    target = communityClient.get_community(community_pk=target)
    communityClient.set_target(target=target)
    action, result = communityClient.add_role(role_name=role_name)
    return JsonResponse({
        "action_status": "success" if action.resolution.status == "implemented" else "error",
        "action_log": action.resolution.log
    })