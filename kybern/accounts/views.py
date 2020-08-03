from django.views import generic
from django.urls import reverse
from django_registration.backends.activation.views import RegistrationView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect

from accounts.models import Profile
from groups.client import GroupClient
from accounts.forms import RegistrationFormWithCode


def myview(request):
    return HttpResponseRedirect(reverse('arch-summary', args=[1945]))


class RegistrationViewWithCode(RegistrationView):
    form_class = RegistrationFormWithCode
    success_url = "/register/complete/"


class IndexView(generic.TemplateView):
    template_name = 'accounts/index.html'


class ProfileView(LoginRequiredMixin, generic.DetailView):
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
