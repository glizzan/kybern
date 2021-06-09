import json

from django.views import generic
from django.urls import reverse, get_resolver
from django_registration.backends.activation.views import RegistrationView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse

from concord.utils.helpers import Client
from concord.actions.models import TemplateModel

from groups.models import Group
from groups.views import serialize_template_for_vue, process_action, get_urls

from accounts.models import Profile, NotificationsSettings, Notification
from accounts.forms import RegistrationFormCleanEmail


class RegistrationViewWithCode(RegistrationView):
    form_class = RegistrationFormCleanEmail
    success_url = "/register/complete/"


class IndexView(generic.TemplateView):
    template_name = 'accounts/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["groups"] = Group.objects.all()
        context["hide_info"] = True if self.request.GET.get("hide_info", None) else False
        return context


def serialize_group(group):
    return {"name": group.name, "pk": group.pk, "group_description": group.group_description}


def get_serialized_notifications(user):
    notifications = []
    for n in Notification.objects.filter(user=user):
        group = n.action.target.get_owner()
        notifications.append({
            "created": str(n.created), "sent": n.sent, "notes": n.notes, "action": process_action(n.action),
            "group_name": group.name, "group_pk": group.pk
        })
    return notifications


class ProfileView(LoginRequiredMixin, generic.DetailView):
    model = Profile
    template_name = 'accounts/profile.html'

    def get_object(self):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = Client(actor=self.request.user)
        leader_list, member_list = client.Community.get_communities_for_user(user_pk=self.request.user.pk, split=True)
        scheme = "https://" if self.request.is_secure() else "http://"
        base_url = scheme + self.request.get_host() + "/"
        initial_state = {
            "user_pk": self.request.user.pk,
            "user_name": self.request.user.username,
            "is_authenticated": self.request.user.is_authenticated,
            "leadership_groups": [serialize_group(group) for group in leader_list],
            "other_groups": [serialize_group(group) for group in member_list],
            "notifications": get_serialized_notifications(self.request.user),
            "base_url": base_url,
            "notifications_url": base_url + get_resolver(None).reverse("profile_update_notifications"),
            "initial_notification_settings": {
                "email_options": [{"value": choice[0], "text": choice[1]} for choice in NotificationsSettings.EMAIL_CHOICES],
                "email_selected": self.request.user.notify_settings.send_emails,
                "everything": self.request.user.notify_settings.always_notify_everything,
                "creator": self.request.user.notify_settings.always_notify_creator,
                "approval": self.request.user.notify_settings.always_notify_approval,
                "resolved": self.request.user.notify_settings.always_notify_action_resolved
            }
        }
        context["initial_state"] = json.dumps(initial_state)
        return context


def update_notifications_settings(request):
    """Updates user's notifications setting based on request from front end."""

    data = json.loads(request.body.decode('utf-8'))

    request.user.notify_settings.send_emails = data.get("email_selected")
    request.user.notify_settings.always_notify_everything = bool(data.get("everything"))
    request.user.notify_settings.always_notify_creator = bool(data.get("creator"))
    request.user.notify_settings.always_notify_approval = bool(data.get("approval"))
    request.user.notify_settings.always_notify_action_resolved = bool(data.get("resolved"))

    request.user.notify_settings.save()

    return JsonResponse({
        "email_selected": request.user.notify_settings.send_emails,
        "everything": request.user.notify_settings.always_notify_everything,
        "creator": request.user.notify_settings.always_notify_creator,
        "approval": request.user.notify_settings.always_notify_approval,
        "resolved": request.user.notify_settings.always_notify_action_resolved
    })


class TemplateLibraryView(generic.ListView):
    model = TemplateModel
    template_name = 'accounts/template_library.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        templates = [serialize_template_for_vue(t, pk_as_key=False) for t in TemplateModel.objects.all()]
        template_community = Client().Community.get_community(community_name="Kybern Template Community")
        initial_state = {
            "user_name": self.request.user.username,
            "user_pk": self.request.user.pk,
            "is_authenticated": self.request.user.is_authenticated,
            "templates": templates,
            "group_pk": template_community.pk,
            "group_name": template_community.name,
            "group_description": template_community.group_description,
            "urls": get_urls(target=template_community.pk),
        }
        context["initial_state"] = json.dumps(initial_state)
        return context

