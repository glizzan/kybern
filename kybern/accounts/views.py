from django.views import generic
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User


from accounts.models import Profile


class IndexView(generic.TemplateView):
    template_name = 'accounts/index.html'


class ProfileView(generic.DetailView):
    model = Profile
    template_name = 'accounts/profile.html'

    def get_object(self):
        return self.request.user.profile
