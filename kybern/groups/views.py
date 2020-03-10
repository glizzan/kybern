from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import Group


class GroupListView(generic.ListView):
    model = Group
    template_name = 'groups/group_list.html'


class GroupDetailView(generic.DetailView):
    model = Group
    template_name = 'groups/group_detail.html'


class GroupCreateView(generic.edit.CreateView):
    model = Group
    template_name = 'groups/group_create.html'
    fields = ['name', 'group_description', 'governing_permission_enabled',
        'foundational_permission_enabled']

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.save()
        return HttpResponseRedirect(reverse('group_detail', kwargs={'pk': self.object.pk}))
