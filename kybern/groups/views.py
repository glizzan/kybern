import json, logging, csv
from contextlib import suppress

from django.urls import reverse, get_resolver, exceptions
from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.views import generic
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse

from concord.actions.models import TemplateModel
from concord.resources.models import Comment, SimpleList, CommentCatcher
from concord.permission_resources.models import PermissionsItem
from concord.utils.lookups import get_all_dependent_fields
from concord.utils.helpers import Client, Changes

from accounts.models import User
from .models import Group, Forum, Post
from .decorators import reformat_input_data


logger = logging.getLogger(__name__)


##################################
### Helper methods and classes ###
##################################


def get_urls(target=None):

    resolver = get_resolver(None)
    url_map = {}

    for url_name in resolver.reverse_dict.keys():

        if isinstance(url_name, str):

            with suppress(exceptions.NoReverseMatch):
                url = resolver.reverse(url_name)
                url_map.update({url_name: url})
                continue

            with suppress(exceptions.NoReverseMatch):
                if target:
                    url = resolver.reverse(url_name, target=target)
                    url_map.update({url_name: url})
                    continue

    return {key: value for key, value in url_map.items() if "groups/" in value}


def generate_url_map(request, target=None):
    return JsonResponse({"urls": get_urls(target)})


def get_model(model_name):
    for app_config in apps.get_app_configs():
        try:
            model = app_config.get_model(model_name)
            return model
        except LookupError:
            pass


def process_action(action):
    """Method for getting action data.  The action provided is always valid."""

    if action.status == "implemented":
        action_verb = ""
        follow_up = f"They did so because they have the permission {action.approved_through()}."
    else:
        action_verb = "tried to "
        follow_up = ""

    action_time = action.created_at.strftime("%b %d %Y %I:%M%p")
    if action.target:
        action_description = f"{action.change.description_past_tense()} {action.target.get_name()}"
    else:
        action_description = action.change.description_past_tense()

    action_string = f"At {action_time}, {action.actor.username} {action_verb}{action_description}. {follow_up}"

    conditions = Client().Conditional.get_condition_items_for_action(action_pk=action.pk)

    return {
        "action_pk": action.pk,
        "action_target_pk": action.object_id,
        "action_target_model": action.target.__class__.__name__,   # will this work???
        "action_target_content_type": action.content_type.pk,
        "description": action.get_description(with_actor=False, with_target=False),
        "created": str(action.created_at),
        "display_date": action_time,
        "actor": action.actor.username,
        "actor_pk": action.actor.pk,
        "status": action.status,
        "resolution_passed_by": action.approved_through(),
        "display": action_string,
        "is_template": action.change.get_change_type() == Changes().Actions.ApplyTemplate,
        "template_description": action.get_template_info(),
        "has_condition": {
            "exists": True if conditions else False,
            "conditions": [{"pk": condition.pk, "type": condition.__class__.__name__,
                           "passing_description": condition.description_for_passing_condition()}
                           for condition in conditions]
        }
    }


def get_action_dict(action, fetch_template_actions=False):
    """Helper method to unpack action information to make it readable for vue/javascript.  Note that
    unlike process_action, which is always called regarding existing actions, get_action_dict
    may be passed an invalid action."""

    if action.status == "invalid":
        return {
            "action_status": "invalid",
            "user_message": action.error_message,
            "action_developer_log": action.error_message
        }

    action_created = True if action.status in ["implemented", "approved", "waiting", "rejected"] else False
    return {
        "action_created": action_created,
        "action_status": action.status,
        "action_pk": action.pk,
        "is_template": action.change.get_change_type() == Changes().Actions.ApplyTemplate,
        # text
        "action_description": action.get_description(with_actor=False, with_target=False),
        "user_message": action.rejection_reason(),
        "action_developer_log": action.get_logs()
    }


def get_multiple_action_dicts(actions):
    # overall data
    action_log = ""
    action_status = "implemented"
    for action in actions:
        if action.status != "implemented":
            action_status = "error"
            action_log += action.get_logs() if action.get_logs() else ""
    # individual action data
    action_dicts_list = []
    for action in actions:
        action_dicts_list.append(get_action_dict(action))

    return {
        "multiple_actions": True,
        "action_status": action_status,
        "action_log": action_log,
        "actions": action_dicts_list
    }


def serialize_existing_permission_for_vue(permission, pk_as_key=True):
    """  (note: this matches format specified in vuex store)
    permissions: {{permissions }},
        // {int(pk) : {name: x, display: x, change_type: x } } """

    if hasattr(permission.permitted_object, "is_community"):
        target = "community"
    else:
        target = f"{permission.permitted_object.__class__.__name__} '{permission.permitted_object.get_name()}'"

    owner_permission = False
    if permission.permitted_object.foundational_permission_enabled or permission.get_state_change_object().is_foundational:
        owner_permission = True

    governor_permission = not owner_permission and permission.permitted_object.governing_permission_enabled

    permission_dict = {
        "name": permission.change_display_string(),
        "display": permission.display_string(),
        "change_name": permission.change_name(),
        "change_type": permission.change_type,
        "actors": permission.get_actors(),
        "is_foundational": permission.is_foundational(),
        "section": permission.get_section(),
        "roles": permission.get_roles(),
        "anyone": permission.anyone,
        "pk": permission.pk,
        "change_field_options": permission.get_change_fields(),
        "dependent_field_options": permission.get_context_keys(),
        "owner_permission": owner_permission,
        "governor_permission": governor_permission,
        "target": target,
        "linked": permission.get_state_change_object().linked_filters
    }

    condition_data = permission.get_condition_data() if permission.has_condition() else None
    permission_dict.update({"condition": condition_data})

    if pk_as_key:
        return {permission.pk: permission_dict}
    return permission_dict


def serialize_existing_comment_for_vue(comment):
    """ Serializes comment from Django model to JSOn-serializable dict.
    (note: this matches format specified in vuex store)
    """
    return {
        comment.pk: {
            'pk': comment.pk, 'text': comment.text, 'commentor_pk': comment.commentor.pk,
            'created_at': comment.created_at, 'updated_at': comment.updated_at
        }
    }


def serialize_forum_for_vue(forum):
    return {'pk': forum.pk, 'name': forum.name, 'description': forum.description, 'special': forum.special}


def serialize_post_for_vue(post):
    return {
        'pk': post.pk, 'title': post.title, 'content': post.content, 'forum_pk': post.forum.pk,
        'created': post.created, 'author': post.author.pk
    }


def serialize_forums_for_vue(forums):

    forum_list = []
    for forum in forums:
        forum_list.append(serialize_forum_for_vue(forum))

    return forum_list


def serialize_list_for_vue(simple_list):
    return {'pk': simple_list.pk, 'name': simple_list.name, 'description': simple_list.description,
            'configuration': simple_list.get_row_configuration(), 'rows': simple_list.get_rows()}


def serialize_lists_for_vue(simple_lists):
    serialized_lists = []
    for simple_list in simple_lists:
        serialized_lists.append(serialize_list_for_vue(simple_list))
    return serialized_lists


def serialize_document_for_vue(document):
    return {'pk': document.pk, 'name': document.name, 'description': document.description, 'content': document.content}


def serialize_documents_for_vue(documents):
    serialized_docs = []
    for document in documents:
        serialized_docs.append(serialize_document_for_vue(document))
    return serialized_docs


def serialize_template_for_vue(template, pk_as_key=True):
    template_dict = {
        "pk": template.pk,
        "name": template.name,
        "description": template.user_description,
        "supplied_fields": template.get_supplied_form_fields(),
        "action_breakdown": template.get_template_breakdown(),
        "scopes": template.get_scopes()
    }
    if pk_as_key:
        return {template.pk: template_dict}
    return template_dict


############################
### Standard Django CBVs ###
############################


class GroupDetailView(LoginRequiredMixin, generic.DetailView):
    model = Group
    template_name = 'groups/group_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        initial_state = {
            "urls": get_urls(target=self.object.pk),
            "group_pk": self.object.pk,
            "group_name": self.object.name,
            "group_description": self.object.group_description,
            "user_pk": self.request.user.pk,
            "user_name": self.request.user.username,
            "is_authenticated": self.request.user.is_authenticated
        }
        context["initial_state"] = json.dumps(initial_state)
        return context


class GroupCreateView(LoginRequiredMixin, generic.TemplateView):
    template_name = "groups/group_create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        initial_state = {
            "urls": get_urls(),
            "user_name": self.request.user.username,
            "user_pk": self.request.user.pk,
            "is_authenticated": self.request.user.is_authenticated
        }
        context["initial_state"] = json.dumps(initial_state)
        return context


class GroupListView(LoginRequiredMixin, generic.ListView):
    model = Group
    template_name = 'groups/group_list.html'


##############################
### Views for getting data ###
##############################

@login_required
def get_governance_data(request, target):

    client = Client(actor=request.user)
    default_target = client.Community.get_community(community_pk=target)
    client.update_target_on_all(target=default_target)

    roles = [{'name': role_name, 'current_members': role_data}
             for role_name, role_data in client.Community.get_custom_roles().items()]

    governance_data = {

        # leadership info
        "owners": client.Community.target.roles.get_owners(),
        "governors": client.Community.target.roles.get_governors(),
        "governance_info": json.dumps(client.Community.get_governance_info_as_text()),

        # role/member info
        "roles": roles,
        "current_members": [member.pk for member in client.Community.get_members()],
        "users": [{'name': person.username, 'pk': person.pk} for person in User.objects.all()]

    }

    return JsonResponse({"governance_data": governance_data})


def get_permission_options(client):
    """  This method gets permission *options*, not the permission data itself, which is fetched
    as needed based on user action.

    (note: this matches format specified in vuex store)
    permission_options: {{ permission_options}},
        // {model_name: [ { value: x , text: x} ], model_name: [ { value: x , text: x}  ]}
    """

    permission_options = {}

    for model_class in [Group, Forum, Post, Comment, PermissionsItem, SimpleList]:

        # get settable permissions given model class
        settable_permissions = client.PermissionResource.get_settable_permissions_for_model(model_class)

        # get a list of permission options and save to permission_options under the model name
        model_string = model_class.__name__.lower()
        permission_options[model_string] = []
        for state_change in settable_permissions:
            permission_options[model_string].append({
                "value": state_change.get_change_type(),
                "text": state_change.change_description(),
                "group": state_change.section
            })

    return permission_options


def get_condition_options(client):
    """ This method gets condition *options* and configuration *options*, not data for
    existing conditions. (note: this matches format specified in vuex store)

    condition_options: {{ condition_options }},
        // [ { value: x , text: x } ]
    condition_configuration_options: {{ condition_configuration_options }},
        // { fieldname: { display: x, type: x, required: x, value: x, field_name: x } }
    """

    # Get condition options
    settable_conditions = client.Conditional.get_possible_conditions()
    condition_options = []
    for cond in settable_conditions:
        condition_options.append({
            "value": cond.__name__,
            "text": cond.descriptive_name,
            "linked": False if not hasattr(cond, "linked") else cond.linked
        })

    # Create condition configuration
    condition_configuration = {}
    for condition in settable_conditions:
        condition_configuration.update({condition.__name__: condition.get_configurable_fields()})

    return condition_options, condition_configuration


@login_required
def get_permission_data(request, target):

    client = Client(actor=request.user)
    default_target = client.Community.get_community(community_pk=target)
    client.update_target_on_all(target=default_target)

    permission_options = get_permission_options(client)
    condition_options, condition_configuration_options = get_condition_options(client)
    dependent_field_options = get_all_dependent_fields()
    owner_condition = client.Community.get_condition_data(leadership_type="owner")
    governor_condition = client.Community.get_condition_data(leadership_type="governor")

    return JsonResponse({
        "permission_options": permission_options,
        "condition_options": condition_options,
        "condition_configuration_options": condition_configuration_options,
        "dependent_field_options": dependent_field_options,
        "owner_condition": owner_condition,
        "governor_condition": governor_condition
    })


@login_required
def get_forum_data(request, target):

    client = Client(actor=request.user)
    default_target = client.Community.get_community(community_pk=target)
    client.update_target_on_all(target=default_target)

    return JsonResponse({
        "forums": serialize_forums_for_vue(client.Forum.get_forums_owned_by_target())
    })


####################
### Group Views ###
####################


@login_required
def create_group(request):
    request_data = json.loads(request.body.decode('utf-8'))
    group_name = request_data.get("group_name")
    group_description = request_data.get("group_description")

    client = Client(actor=request.user)
    community = client.Community.create_community(name=group_name)

    # add description - need to do this separately as create_community is a Concord method that doesn't know about the
    # Group description field
    client.Community.set_target(community)
    client.Community.change_group_description(group_description=group_description)

    return JsonResponse({"group_pk": community.pk})


@login_required
def change_group_name(request):

    request_data = json.loads(request.body.decode('utf-8'))
    group_pk = request_data.get("group_pk")
    new_name = request_data.get("new_name")

    client = Client(actor=request.user)
    target = client.Community.get_community(community_pk=group_pk)
    client.Community.set_target(target=target)

    action, result = client.Community.change_name_of_community(name=new_name)
    action_dict = get_action_dict(action)
    action_dict["group_name"] = new_name
    return JsonResponse(action_dict)


@login_required
def change_group_description(request):

    request_data = json.loads(request.body.decode('utf-8'))
    group_pk = request_data.get("group_pk")
    group_description = request_data.get("group_description")

    client = Client(actor=request.user)
    target = client.Community.get_community(community_pk=group_pk)
    client.Community.set_target(target=target)

    action, result = client.Community.change_group_description(group_description=group_description)
    action_dict = get_action_dict(action)
    action_dict["group_description"] = group_description
    return JsonResponse(action_dict)


####################
### Forums Views ###
####################


@login_required
def get_forums(request, target):

    client = Client(actor=request.user)
    target = client.Community.get_community(community_pk=target)
    client.update_target_on_all(target=target)

    forums = client.Forum.get_forums_owned_by_target()
    forum_list = serialize_forums_for_vue(forums)

    return JsonResponse({"forums": forum_list})


@login_required
def get_forum(request, target):

    request_data = json.loads(request.body.decode('utf-8'))
    forum_pk = request_data.get("forum_pk")

    client = Client(actor=request.user)
    forum = client.Forum.get_forum_given_pk(forum_pk)

    return JsonResponse({'forum_data': serialize_forum_for_vue(forum)})


@login_required
def add_forum(request, target):

    client = Client(actor=request.user)
    target = client.Community.get_community(community_pk=target)
    client.update_target_on_all(target=target)

    request_data = json.loads(request.body.decode('utf-8'))
    name = request_data.get("name")
    description = request_data.get("description", None)

    action, result = client.Forum.add_forum(name=name, description=description)

    action_dict = get_action_dict(action)
    if action.status == "implemented":
        action_dict["created_instance"] = serialize_forum_for_vue(result)
    return JsonResponse(action_dict)


@login_required
def edit_forum(request, target):

    request_data = json.loads(request.body.decode('utf-8'))
    pk = request_data.get("pk")
    name = request_data.get("name", None)
    description = request_data.get("description", None)

    client = Client(actor=request.user)
    forum = client.Forum.get_forum_given_pk(pk)
    client.Forum.set_target(target=forum)

    action, result = client.Forum.edit_forum(name=name, description=description)

    action_dict = get_action_dict(action)
    if action.status == "implemented":
        action_dict["edited_instance"] = serialize_forum_for_vue(result)
    return JsonResponse(action_dict)


@login_required
def delete_forum(request, target):

    request_data = json.loads(request.body.decode('utf-8'))
    pk = request_data.get("pk")

    client = Client(actor=request.user)
    forum = client.Forum.get_forum_given_pk(pk)
    client.Forum.set_target(target=forum)

    action, result = client.Forum.delete_forum()

    action_dict = get_action_dict(action)
    action_dict["deleted_forum_pk"] = pk
    return JsonResponse(action_dict)


@login_required
def get_posts_for_forum(request, target):

    request_data = json.loads(request.body.decode('utf-8'))
    forum_pk = request_data.get("forum_pk")

    client = Client(actor=request.user)
    forum = client.Forum.get_forum_given_pk(forum_pk)
    client.Forum.set_target(target=forum)
    posts = client.Forum.get_posts_for_forum()

    serialized_posts = [serialize_post_for_vue(post) for post in posts]

    return JsonResponse({'forum_pk': forum_pk, 'posts': serialized_posts})


@login_required
def get_post(request, target):

    request_data = json.loads(request.body.decode('utf-8'))
    post_pk = request_data.get("post_pk")

    client = Client(actor=request.user)
    post = client.Forum.get_post_given_pk(pk=post_pk)

    return JsonResponse({'post': serialize_post_for_vue(post)})


@login_required
def add_post(request, target):

    request_data = json.loads(request.body.decode('utf-8'))
    forum_pk = request_data.get("forum_pk")
    title = request_data.get("title")
    content = request_data.get("content", None)

    client = Client(actor=request.user)
    forum = client.Forum.get_forum_given_pk(forum_pk)
    client.Forum.set_target(target=forum)

    action, result = client.Forum.add_post(title=title, content=content)

    action_dict = get_action_dict(action)
    if action.status == "implemented":
        action_dict["created_instance"] = serialize_post_for_vue(result)
    return JsonResponse(action_dict)


@login_required
def edit_post(request, target):

    request_data = json.loads(request.body.decode('utf-8'))
    pk = request_data.get("pk")
    title = request_data.get("title", None)
    content = request_data.get("content", None)

    client = Client(actor=request.user)
    post = client.Forum.get_post_given_pk(pk)
    client.Forum.set_target(target=post)

    action, result = client.Forum.edit_post(title=title, content=content)

    action_dict = get_action_dict(action)
    if action.status == "implemented":
        action_dict["edited_instance"] = serialize_post_for_vue(result)
    return JsonResponse(action_dict)


@login_required
def delete_post(request, target):

    request_data = json.loads(request.body.decode('utf-8'))
    pk = request_data.get("pk")

    client = Client(actor=request.user)
    post = client.Forum.get_post_given_pk(pk)
    client.Forum.set_target(target=post)

    action, result = client.Forum.delete_post()

    action_dict = get_action_dict(action)
    action_dict["deleted_post_pk"] = pk
    return JsonResponse(action_dict)


################################################################################
### Helper methods, likely to be moved to concord, called by vuex data store ###
################################################################################


@login_required
def add_role(request, target):

    request_data = json.loads(request.body.decode('utf-8'))

    client = Client(actor=request.user)
    target = client.Community.get_community(community_pk=target)
    client.update_target_on_all(target=target)

    action, result = client.Community.add_role_to_community(role_name=request_data['role_name'])

    return JsonResponse(get_action_dict(action))


@login_required
def remove_role(request, target):

    request_data = json.loads(request.body.decode('utf-8'))

    client = Client(actor=request.user)
    target = client.Community.get_community(community_pk=target)
    client.update_target_on_all(target=target)

    action, result = client.Community.remove_role_from_community(role_name=request_data['role_name'])

    return JsonResponse(get_action_dict(action))


@login_required
def add_members(request, target):

    request_data = json.loads(request.body.decode('utf-8'))

    client = Client(actor=request.user)
    target = client.Community.get_community(community_pk=target)
    client.update_target_on_all(target=target)

    action, result = client.Community.add_members_to_community(member_pk_list=request_data["user_pks"])

    return JsonResponse(get_action_dict(action))


@login_required
def remove_members(request, target):

    request_data = json.loads(request.body.decode('utf-8'))

    client = Client(actor=request.user)
    target = client.Community.get_community(community_pk=target)
    client.update_target_on_all(target=target)

    action, result = client.Community.remove_members_from_community(member_pk_list=request_data['user_pks'])

    return JsonResponse(get_action_dict(action))


@login_required
def add_people_to_role(request, target):

    request_data = json.loads(request.body.decode('utf-8'))

    client = Client(actor=request.user)
    target = client.Community.get_community(community_pk=target)
    client.update_target_on_all(target=target)

    action, result = client.Community.add_people_to_role(
        role_name=request_data['role_name'],
        people_to_add=request_data['user_pks']
    )

    return JsonResponse(get_action_dict(action))


@login_required
def remove_people_from_role(request, target):

    request_data = json.loads(request.body.decode('utf-8'))

    client = Client(actor=request.user)
    target = client.Community.get_community(community_pk=target)
    client.update_target_on_all(target=target)

    action, result = client.Community.remove_people_from_role(
        role_name=request_data['role_name'],
        people_to_remove=request_data['user_pks']
    )

    return JsonResponse(get_action_dict(action))


####################################
### Condition & permission views ###
####################################


@transaction.non_atomic_requests
def get_permissions_given_role(actor, target, role_name):

    client = Client(actor=actor, target=target)

    existing_permissions = client.PermissionResource.get_permissions_associated_with_role_for_target(role_name=role_name)

    permission_pks, permissions = [], {}
    for permission in existing_permissions:
        permission_pks.append(permission.pk)
        permissions.update(serialize_existing_permission_for_vue(permission))

    return permission_pks, permissions


@transaction.non_atomic_requests
@login_required
def get_data_for_role(request, target):

    client = Client(actor=request.user)
    target = client.Community.get_community(community_pk=target)

    request_data = json.loads(request.body.decode('utf-8'))
    role_name = request_data['role_name']

    permission_pks, permissions = get_permissions_given_role(request.user, target, role_name)

    return JsonResponse({"permissions": permissions, "role_permissions": permission_pks})


def get_permission_info(permission):
    return {
        "pk": permission.pk,
        "permission_data": list(serialize_existing_permission_for_vue(permission).values())
    }


@login_required
@reformat_input_data
def add_permission(request, target, permission_type, item_or_role, permission_actors=None,
                   permission_roles=None, item_id=None, item_model=None):

    if item_or_role == "item":    # If an item has been passed in, make it the target
        model_class = get_model(item_model)
        target = model_class.objects.get(pk=item_id)
    if item_or_role == "role":    # Otherwise the role the community is set on is the target
        target = Client(actor=request.user).Community.get_community(community_pk=target)

    client = Client(actor=request.user, target=target)

    action, result = client.PermissionResource.add_permission(
        change_type=permission_type, actors=permission_actors, roles=permission_roles)

    action_dict = get_action_dict(action)
    permission_info = get_permission_info(result) if action.status == "implemented" else None
    action_dict.update({"permission": permission_info, "item_id": item_id, "item_model": item_model})
    return JsonResponse(action_dict)


@login_required
@reformat_input_data
def update_permission(request, target, permission_id, permission_actors=None, permission_roles=None):

    client = Client(actor=request.user)
    target_permission = client.PermissionResource.get_permission(pk=permission_id)

    actions = []

    if permission_actors:
        actor_actions = client.PermissionResource.update_actors_on_permission(
            actor_data=permission_actors, permission=target_permission
        )
        actions += actor_actions
    if permission_roles:
        role_actions = client.PermissionResource.update_roles_on_permission(
            role_data=permission_roles, permission=target_permission
        )
        actions += role_actions

    action_dict = get_multiple_action_dicts(actions)

    permission = client.PermissionResource.get_permission(pk=permission_id)  # get refreshed version
    permission_info = get_permission_info(permission)
    action_dict.update({"permission": permission_info})

    return JsonResponse(action_dict)


@login_required
@reformat_input_data
def delete_permission(request, target, permission_id):

    client = Client(actor=request.user, target=target)
    permission = client.PermissionResource.get_permission(pk=permission_id)
    client.update_target_on_all(permission)

    # now remove permission
    action, result = client.PermissionResource.remove_permission()
    action_dict = get_action_dict(action)
    action_dict.update({"removed_permission_pk": permission_id})
    return JsonResponse(action_dict)


####################################
### Views for setting conditions ###
####################################


@login_required
@reformat_input_data
def add_condition(request, target, condition_type, permission_or_leadership,
                  target_permission_id=None, leadership_type=None, condition_data=None,
                  permission_data=None):

    client = Client(actor=request.user)

    if permission_or_leadership == "permission":

        target = client.PermissionResource.get_permission(pk=target_permission_id)
        client.update_target_on_all(target)

        action, result = client.Conditional.add_condition(
            condition_type=condition_type, condition_data=condition_data, permission_data=permission_data)

        if action.status == "implemented":
            condition_data = target.get_condition_data()

    elif permission_or_leadership == "leadership":

        target = client.Community.get_community(community_pk=target)
        client.update_target_on_all(target)

        action, result = client.Conditional.add_condition(
            condition_type=condition_type, leadership_type=leadership_type,
            condition_data=condition_data, permission_data=permission_data
        )
        if action.status == "implemented":
            condition_data = target.get_condition_data(leadership_type=leadership_type)

    action_dict = get_action_dict(action)
    action_dict.update({
        "condition_info": condition_data, "permission_or_leadership": permission_or_leadership,
        "leadership_type": leadership_type, "target_permission_id": target_permission_id
    })
    return JsonResponse(action_dict)


@login_required
@reformat_input_data
def edit_condition(request, target, permission_or_leadership, element_id, target_permission_id=None,
                   leadership_type=None, condition_data=None, permission_data=None):

    client = Client(actor=request.user)

    if permission_or_leadership == "permission":

        target = client.PermissionResource.get_permission(pk=target_permission_id)
        client.update_target_on_all(target)

        action, result = client.Conditional.edit_condition(
            element_id=element_id, condition_data=condition_data, permission_data=permission_data)

        if action.status == "implemented":
            condition_data = target.get_condition_data()

    elif permission_or_leadership == "leadership":

        target = client.Community.get_community(community_pk=target)
        client.update_target_on_all(target)

        action, result = client.Conditional.edit_condition(
            element_id=element_id, leadership_type=leadership_type,
            condition_data=condition_data, permission_data=permission_data
        )
        if action.status == "implemented":
            condition_data = target.get_condition_data(leadership_type=leadership_type)

    action_dict = get_action_dict(action)
    action_dict.update({
        "condition_info": condition_data, "permission_or_leadership": permission_or_leadership,
        "leadership_type": leadership_type, "target_permission_id": target_permission_id
    })
    return JsonResponse(action_dict)


@login_required
@reformat_input_data
def remove_condition(request, target, permission_or_leadership, target_permission_id=None, leadership_type=None,
                     element_id=None):

    client = Client(actor=request.user)

    if permission_or_leadership == "permission":
        target = client.PermissionResource.get_permission(pk=target_permission_id)
        client.update_target_on_all(target)
        action, result = client.Conditional.remove_condition(element_id=element_id)
    elif permission_or_leadership == "leadership":
        target = client.Community.get_community(community_pk=target)
        client.update_target_on_all(target)
        action, result = client.Conditional.remove_condition(leadership_type=leadership_type, element_id=element_id)

    # TODO: pass in permission to get form data, if it's set on a permission
    result = result.get_condition_form_data() if result else result

    action_dict = get_action_dict(action)
    action_dict.update({
        "permission_or_leadership": permission_or_leadership, "leadership_type": leadership_type,
        "target_permission_id": target_permission_id, "condition_info": result
    })
    return JsonResponse(action_dict)


#############################################
### Views for interacting with conditions ###
#############################################


@login_required
def update_approval_condition(request):

    request_data = json.loads(request.body.decode('utf-8'))
    condition_pk = request_data.get("condition_pk", None)
    action_to_take = request_data.get("action_to_take", None)

    approvalClient = Client(actor=request.user).Conditional.\
        get_condition_as_client(condition_type="ApprovalCondition", pk=condition_pk)

    if action_to_take == "approve":
        action, result = approvalClient.approve()
    elif action_to_take == "reject":
        action, result = approvalClient.reject()

    return JsonResponse(get_action_dict(action))


@login_required
def update_vote_condition(request):

    request_data = json.loads(request.body.decode('utf-8'))
    condition_pk = request_data.get("condition_pk", None)
    action_to_take = request_data.get("action_to_take", None)

    voteClient = Client(actor=request.user).Conditional.\
        get_condition_as_client(condition_type="VoteCondition", pk=condition_pk)

    action, result = voteClient.vote(vote=action_to_take)

    return JsonResponse(get_action_dict(action))


@login_required
def update_consensus_condition(request):

    request_data = json.loads(request.body.decode('utf-8'))
    condition_pk = request_data.get("condition_pk", None)
    action_to_take = request_data.get("action_to_take", None)
    response = request_data.get("response", None)

    consensusClient = Client(actor=request.user).Conditional.\
        get_condition_as_client(condition_type="ConsensusCondition", pk=condition_pk)

    if action_to_take == "respond":
        action, result = consensusClient.respond(response=response)
    elif action_to_take == "resolve":
        action, result = consensusClient.resolve()

    return JsonResponse(get_action_dict(action))


@transaction.non_atomic_requests
@login_required
def get_conditional_data(request):

    request_data = json.loads(request.body.decode('utf-8'))
    condition_pk = request_data.get("condition_pk", None)
    condition_type = request_data.get("condition_type", None)

    client = Client(actor=request.user)
    condition = client.Conditional.get_condition_item(condition_pk=condition_pk, condition_type=condition_type)

    # for permission on condition, does user have permission?
    permission_details = {}
    for permission in client.PermissionResource.get_permissions_on_object(target_object=condition):
        has_permission = client.PermissionResource.actor_satisfies_permission(
            actor=request.user, permission=permission
        )
        permission_details.update({permission.change_type: has_permission})
    permission_details.update({'user_condition_status': condition.user_condition_status(user=request.user)})

    return JsonResponse({
        "permission_details": permission_details,
        "condition_details": {
            "status": condition.condition_status(),
            "display_status": condition.display_status(),
            "fields": condition.display_fields()
        }
    })


@login_required
def get_action_data(request):

    request_data = json.loads(request.body.decode('utf-8'))
    action_pk = request_data.get("action_pk", None)

    action = Client(actor=request.user).Action.get_action_given_pk(action_pk)

    return JsonResponse({"action_data": process_action(action)})


@login_required
def get_action_data_for_target(request):

    request_data = json.loads(request.body.decode('utf-8'))

    item_id = request_data.get("item_id")
    model_class = get_model(request_data.get("item_model"))
    target = model_class.objects.get(pk=item_id)

    client = Client(actor=request.user, target=target)
    actions = client.Action.get_action_history_given_target()

    return JsonResponse({"action_data": [process_action(action) for action in actions]})


####################################
### Views for leadership include ###
####################################


@login_required
def update_owners(request, target):

    request_data = json.loads(request.body.decode('utf-8'))
    owner_roles = request_data.get("owner_roles", "")  # no need to make into list, leadershipcomponent handles that
    owner_actors = request_data.get("owner_actors", "")  # no need to make into list, leadershipcomponent handles that

    client = Client(actor=request.user)
    target = client.Community.get_community(community_pk=target)
    client.update_target_on_all(target)

    actions = client.Community.update_owners(new_owner_data={"individuals": owner_actors, "roles": owner_roles})

    action_dict = get_multiple_action_dicts(actions)
    action_dict.update({"governance_info": json.dumps(client.Community.get_governance_info_as_text())})

    return JsonResponse(action_dict)


@login_required
def update_governors(request, target):

    request_data = json.loads(request.body.decode('utf-8'))
    governor_roles = request_data.get("governor_roles", "")
    governor_actors = request_data.get("governor_actors", "")

    client = Client(actor=request.user)
    target = client.Community.get_community(community_pk=target)
    client.update_target_on_all(target)

    actions = client.Community.update_governors(
        new_governor_data={"individuals": governor_actors, "roles": governor_roles}
    )

    action_dict = get_multiple_action_dicts(actions)
    action_dict.update({"governance_info": json.dumps(client.Community.get_governance_info_as_text())})

    return JsonResponse(action_dict)


#############################
### Misc permission views ###
#############################


@login_required
def get_permission(request):

    request_data = json.loads(request.body.decode('utf-8'))

    permission_pk = request_data.get("permission_pk")

    client = Client(actor=request.user)
    permission = client.PermissionResource.get_permission(pk=permission_pk)

    return JsonResponse({"permission_data": serialize_existing_permission_for_vue(permission, pk_as_key=False)})


@transaction.non_atomic_requests
@login_required
def get_permissions(request):

    request_data = json.loads(request.body.decode('utf-8'))

    item_id = request_data.get("item_id")
    model_class = get_model(request_data.get("item_model"))
    target = model_class.objects.get(pk=item_id)

    client = Client(actor=request.user, target=target)

    if hasattr(target, "is_community") and target.is_community:
        existing_permissions = client.PermissionResource.get_all_permissions_in_community(community=target)
    else:
        existing_permissions = client.PermissionResource.get_all_permissions()

    permission_pks, permissions = [], {}
    for permission in existing_permissions:
        permission_pks.append(permission.pk)
        permissions.update(serialize_existing_permission_for_vue(permission))

    nested_pks = []
    for permission in client.PermissionResource.get_nested_permissions(target=target):
        nested_pks.append(permission.pk)
        permissions.update(serialize_existing_permission_for_vue(permission))

    return JsonResponse({
        "item_id": item_id, "item_model": request_data.get("item_model"), "permissions": permissions,
        "permission_pks": permission_pks, "nested_pks": nested_pks,
        "foundational": target.foundational_permission_enabled,
        "governing": target.governing_permission_enabled
    })


@login_required
def change_item_permission_override(request):
    """Helper method to manipulate governing and foundational permissions, aka the permission overrides.
    Takes in item_id and item_model to retrieve the item being acted on, and toggles that indicate
    whether the change is to the foundational or governing permission and whether the override is being
    enabled or disabled."""

    request_data = json.loads(request.body.decode('utf-8'))
    item_id = request_data.get("item_id")
    model_class = get_model(request_data.get("item_model"))
    target = model_class.objects.get(pk=item_id)

    client = Client(actor=request.user, target=target)

    enable_or_disable = request_data.get("enable_or_disable")
    governing_or_foundational = request_data.get("governing_or_foundational")

    if governing_or_foundational == "governing":
        if enable_or_disable == "enable":
            action, result = client.PermissionResource.enable_governing_permission()
        elif enable_or_disable == "disable":
            action, result = client.PermissionResource.disable_governing_permission()
    elif governing_or_foundational == "foundational":
        if enable_or_disable == "enable":
            action, result = client.PermissionResource.enable_foundational_permission()
        elif enable_or_disable == "disable":
            action, result = client.PermissionResource.disable_foundational_permission()

    action_dict = get_action_dict(action)
    action_dict.update({
        "item_id": item_id, "item_model": request_data.get("item_model"),
        "foundational": result.foundational_permission_enabled,
        "governing": result.governing_permission_enabled
    })
    return JsonResponse(action_dict)


@login_required
def toggle_anyone(request, target):

    request_data = json.loads(request.body.decode('utf-8'))
    permission_id = request_data.get("permission_id")
    enable_or_disable = request_data.get("enable_or_disable")

    client = Client(actor=request.user)
    target = client.PermissionResource.get_permission(pk=permission_id)
    client.update_target_on_all(target=target)

    if enable_or_disable == "enable":
        action, result = client.PermissionResource.give_anyone_permission()
    elif enable_or_disable == "disable":
        action, result = client.PermissionResource.remove_anyone_from_permission()

    action_dict = get_action_dict(action)
    action_dict.update({"permission": get_permission_info(result)})

    return JsonResponse(action_dict)


#####################
### Comment views ###
#####################


@login_required
def get_comment_data(request):

    request_data = json.loads(request.body.decode('utf-8'))

    item_id = request_data.get("item_id")
    model_class = get_model(request_data.get("item_model"))
    target = model_class.objects.get(pk=item_id)

    client = Client(actor=request.user, target=target)
    existing_comments = client.Comment.get_all_comments_on_target()

    comment_pks, comments = [], {}
    for comment in existing_comments:
        comment_pks.append(comment.pk)
        comments.update(serialize_existing_comment_for_vue(comment))

    return JsonResponse({
        "item_id": item_id, "item_model": request_data.get("item_model"), "comments": comments,
        "comment_pks": comment_pks
    })


@login_required
def add_comment(request):

    request_data = json.loads(request.body.decode('utf-8'))

    item_id = request_data.get("item_id")
    model_class = get_model(request_data.get("item_model"))
    target = model_class.objects.get(pk=item_id)
    text = request_data.get("text")

    client = Client(actor=request.user, target=target)
    action, result = client.Comment.add_comment(text=text)

    action_dict = get_action_dict(action)
    if result:
        action_dict.update({'comment': serialize_existing_comment_for_vue(result)})
    return JsonResponse(action_dict)


@login_required
def edit_comment(request):

    request_data = json.loads(request.body.decode('utf-8'))
    client = Client(actor=request.user)
    comment = client.Comment.get_comment(pk=int(request_data.get("comment_pk")))
    client.update_target_on_all(comment)

    text = request_data.get("text")
    action, result = client.Comment.edit_comment(text=text)

    action_dict = get_action_dict(action)
    action_dict.update({'comment': serialize_existing_comment_for_vue(result)})
    return JsonResponse(action_dict)


@login_required
def delete_comment(request):

    request_data = json.loads(request.body.decode('utf-8'))
    client = Client(actor=request.user)
    comment_pk = request_data.get("comment_pk")
    comment = client.Comment.get_comment(pk=comment_pk)
    client.update_target_on_all(comment)

    action, result = client.Comment.delete_comment()

    action_dict = get_action_dict(action)
    action_dict.update({'deleted_comment_pk': comment_pk})
    return JsonResponse(action_dict)


######################
### Template Views ###
######################


@login_required
@reformat_input_data(expect_target=False)   # target passed in is empty
def get_templates_for_scope(request, target, scope):
    client = Client(actor=request.user)
    templates = client.Template.get_templates_for_scope(scope=scope)
    template_dict = [serialize_template_for_vue(template, pk_as_key=False) for template in templates]
    response_dict = {'templates': template_dict, 'scope': scope}
    return JsonResponse(response_dict)


@login_required
@reformat_input_data(expect_target=False)
def apply_template(request, target, target_pk, target_model, template_model_pk, supplied_fields=None):

    client = Client(actor=request.user)

    # get target
    target = client.Action.get_object_given_model_and_pk(target_model, int(target_pk))
    client.update_target_on_all(target)

    action, result = client.Template.apply_template(
        template_model_pk=template_model_pk, supplied_fields=supplied_fields
    )

    action_dict = get_action_dict(action)
    return JsonResponse(action_dict)


##################
### List Views ###
##################


@login_required
def get_lists(request, target):

    client = Client(actor=request.user)
    target = client.Community.get_community(community_pk=target)
    client.update_target_on_all(target=target)

    lists = client.List.get_all_lists_given_owner(owner=target)
    serialized_lists = serialize_lists_for_vue(lists)

    return JsonResponse({"lists": serialized_lists})


@login_required
@reformat_input_data
def add_list(request, target, name, configuration, description=None):

    client = Client(actor=request.user)
    target = client.Community.get_community(community_pk=target)
    client.List.set_target(target=target)

    action, result = client.List.add_list(name=name, configuration=configuration,
                                          description=description)

    action_dict = get_action_dict(action)
    if action.status == "implemented":
        action_dict["list_data"] = serialize_list_for_vue(result)
    return JsonResponse(action_dict)


@login_required
@reformat_input_data
def edit_list(request, target, list_pk, name=None, configuration=None, description=None):

    client = Client(actor=request.user)
    target = client.List.get_list(pk=list_pk)
    client.List.set_target(target=target)

    action, result = client.List.edit_list(name=name, configuration=configuration,
                                           description=description)

    action_dict = get_action_dict(action)
    if action.status == "implemented":
        action_dict["list_data"] = serialize_list_for_vue(result)
    return JsonResponse(action_dict)


@login_required
@reformat_input_data
def delete_list(request, target, list_pk):
    client = Client(actor=request.user)
    target = client.List.get_list(pk=list_pk)
    client.List.set_target(target=target)

    action, result = client.List.delete_list()

    action_dict = get_action_dict(action)

    if action.status == "implemented":
        action_dict["deleted_list_pk"] = list_pk
    return JsonResponse(action_dict)


@login_required
@reformat_input_data
def add_row(request, target, list_pk, row_content, index=None):

    client = Client(actor=request.user)
    target = client.List.get_list(pk=list_pk)
    client.List.set_target(target=target)

    action, result = client.List.add_row_to_list(row_content=row_content, index=index)

    return JsonResponse(get_action_dict(action))


@login_required
@reformat_input_data
def edit_row(request, target, list_pk, row_content, index):

    client = Client(actor=request.user)
    target = client.List.get_list(pk=list_pk)
    client.List.set_target(target=target)

    action, result = client.List.edit_row_in_list(row_content=row_content, index=index)

    return JsonResponse(get_action_dict(action))


@login_required
@reformat_input_data
def move_row(request, target, list_pk, old_index, new_index):

    client = Client(actor=request.user)
    target = client.List.get_list(pk=list_pk)
    client.List.set_target(target=target)

    action, result = client.List.move_row_in_list(old_index=old_index, new_index=new_index)

    return JsonResponse(get_action_dict(action))


@login_required
@reformat_input_data
def delete_row(request, target, list_pk, index):

    client = Client(actor=request.user)
    target = client.List.get_list(pk=list_pk)
    client.List.set_target(target=target)

    action, result = client.List.delete_row_in_list(index=index)

    return JsonResponse(get_action_dict(action))


######################
### Document Views ###
######################


@login_required
def get_documents(request, target):

    client = Client(actor=request.user)
    target = client.Community.get_community(community_pk=target)
    client.update_target_on_all(target=target)

    docs = client.Document.get_all_documents_given_owner(owner=target)
    serialized_docs = serialize_documents_for_vue(docs)

    return JsonResponse({"documents": serialized_docs})


@login_required
@reformat_input_data
def add_document(request, target, name, description=None, content=None):

    client = Client(actor=request.user)
    target = client.Community.get_community(community_pk=target)
    client.Document.set_target(target=target)

    action, result = client.Document.add_document(name=name, description=description, content=content)

    action_dict = get_action_dict(action)
    if action.status == "implemented":
        action_dict["created_instance"] = serialize_document_for_vue(result)
    return JsonResponse(action_dict)


@login_required
@reformat_input_data
def edit_document(request, target, document_pk, name=None, description=None, content=None):

    client = Client(actor=request.user)
    target = client.Document.get_document(pk=document_pk)
    client.Document.set_target(target=target)

    action, result = client.Document.edit_document(name=name, description=description, content=content)

    action_dict = get_action_dict(action)
    if action.status == "implemented":
        action_dict["edited_instance"] = serialize_document_for_vue(result)
    return JsonResponse(action_dict)


@login_required
@reformat_input_data
def delete_document(request, target, document_pk):

    client = Client(actor=request.user)
    target = client.Document.get_document(pk=document_pk)
    client.Document.set_target(target=target)

    action, result = client.Document.delete_document()

    action_dict = get_action_dict(action)

    if action.status == "implemented":
        action_dict["deleted_instance_pk"] = document_pk
    return JsonResponse(action_dict)


######################################################################
### Check Permissions Logic (FIXME: desperately needs refactoring) ###
######################################################################


def update_leaders(client, pass_in_client, params, methods_to_try):
    for new_name in methods_to_try:
        result = client.PermissionResource.has_permission(pass_in_client, new_name, params)
        if result:
            return True
    return False


def get_alt_target(client, params):
    # create new client with new target if target is not community
    alt_target = params.pop("alt_target", None) if params else None
    if alt_target:
        model, pk = alt_target.split("_")
        if model == "action":
            """Action is not a PermissionedModel but rarely gets set as target (through
            comments mostly), we automatically give people access to Action comments"""
            return "action"
        return client.Action.get_object_given_model_and_pk(model, int(pk))


@transaction.non_atomic_requests
@reformat_input_data
@login_required
def check_permissions(request, target, permissions):
    """
    Recieves a list of dicts, permissions. Each has a method name and, optionally, parameters and
    an alias. For each permission, check if we have it. Store result under alias if supplied.
    Returns a list of permission names with boolean values indicating whether user has the permissions."""

    client = Client(actor=request.user)
    default_target = client.Community.get_community(community_pk=target)
    client.update_target_on_all(target=default_target)

    permission_dict = {}
    for permission_name, params in permissions.items():

        pass_in_client = Client(actor=request.user, target=default_target)

        alt_target = get_alt_target(client, params)
        if alt_target == "action":
            permission_dict.update({permission_name: True})
            continue
        if alt_target is not None:
            pass_in_client.update_target_on_all(alt_target)

        result = client.PermissionResource.has_permission(pass_in_client, permission_name, params, exclude_conditional=True)
        permission_dict.update({permission_name: result})

    return JsonResponse({"user_permissions": permission_dict})


####################
### Export Views ###
####################


# NOTE: these export views need permission checks


def export_as_csv(request, target):
    """Returns an HTTP Response containing a CSV file. Default for exporting Lists."""

    # get object to export as CSV
    model_class = get_model(request.GET.get("item_model"))
    item = model_class.objects.get(pk=int(request.GET.get("item_id")))

    # export it
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="' + item.get_name() + '.csv"'

    columns, dict_data = item.get_csv_data()

    writer = csv.DictWriter(response, fieldnames=columns)
    writer.writeheader()
    for data in dict_data:
        writer.writerow(data)

    return response


def export_as_json(request, target):
    """Returns an HTTP Response containing a CSV file. Default for exporting Forums."""

    # get object to export as CSV
    model_class = get_model(request.GET.get("item_model"))
    item = model_class.objects.get(pk=int(request.GET.get("item_id")))

    # export it
    response = HttpResponse(item.get_json_data(), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="' + item.get_name() + '.json"'

    return response
