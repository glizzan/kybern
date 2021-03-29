from django.views import generic
from django.urls import reverse
from django_registration.backends.activation.views import RegistrationView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect

from concord.utils.helpers import Client

from accounts.models import Profile
from groups.models import Group
from accounts.forms import RegistrationFormWithCode


class RegistrationViewWithCode(RegistrationView):
    form_class = RegistrationFormWithCode
    success_url = "/register/complete/"


class IndexView(generic.TemplateView):
    template_name = 'accounts/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["groups"] = Group.objects.all()
        context["hide_info"] = True if self.request.GET.get("hide_info", None) else False
        return context


class ProfileView(LoginRequiredMixin, generic.DetailView):
    model = Profile
    template_name = 'accounts/profile.html'

    def get_object(self):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = Client(actor=self.request.user)
        leader_list, member_list = client.Community.get_communities_for_user(user_pk=self.request.user.pk, split=True)
        context["leadership_groups"] = leader_list
        context["other_groups"] = member_list
        return context
