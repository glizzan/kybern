from django.views import generic
from django.http import HttpResponseRedirect, JsonResponse
import json, logging

from django.urls import reverse
from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType

from concord.actions.utils import Client, Changes, get_all_dependent_fields
from concord.actions.models import TemplateModel
from concord.resources.models import Comment, SimpleList, CommentCatcher
from concord.permission_resources.models import PermissionsItem

from accounts.models import User
from .models import Group, Forum, Post
from .decorators import reformat_input_data


logger = logging.getLogger(__name__)


##################################
### Helper methods and classes ###
##################################


def get_model(model_name):
    for app_config in apps.get_app_configs():
        try:
            model = app_config.get_model(model_name)
            return model
        except LookupError:
            pass


readable_log_dict = {
    "action did not meet any permission criteria": "You do not have permission to take this action."
}


def make_action_errors_readable(action):
    """If needed, gets or creates both a developer-friendly (detailed) log and a user-friendly log."""

    if action.status in ["accepted", "implemented"]:  # should be approved, but do we want accepted/approved here at all?
        return "Your action has been implemented.", action.resolution.log     # unlikely to be displayed/accessed
    if action.status == "waiting":
        return "This action cannot be completed until a condition is passed.", action.resolution.log
    if action.status == "rejected":
        return "You do not have permission to take this action", action.resolution.log
    return readable_log_dict.get(action.resolution.log, "We're sorry, there was an error"), action.resolution.log


def process_action(action):
    """Method for getting action data.  The action provided is always valid."""

    if action.status == "implemented":
        action_verb = ""
        follow_up = "They did so because they have the permission %s." % action.resolution.approved_through
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
        "description": action.get_description(),
        "created": str(action.created_at),
        "display_date": action_time,
        "actor": action.actor.username,
        "status": action.status,
        "resolution passed by": action.resolution.approved_through,
        "display": action_string,
        "is_template": action.change.get_change_type() == Changes().Actions.ApplyTemplate,
        "template_description": action.resolution.template_info,
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
            "action_log": action.error_message,
            "action_developer_log": action.error_message
        }

    display_log, developer_log = make_action_errors_readable(action)
    action_created = True if action.status in ["implemented", "approved", "waiting", "rejected"] else False
    return {
        "action_created": action_created,
        "action_status": action.status,
        "action_pk": action.pk,
        "action_log": display_log,
        "action_developer_log": developer_log,
        "is_template": action.change.get_change_type() == Changes().Actions.ApplyTemplate
    }


def get_multiple_action_dicts(actions):
    # overall data
    action_log = ""
    action_status = "implemented"
    for action in actions:
        if action.status != "implemented":
            action_status = "error"
            action_log += action.resolution.log if action.resolution.log else ""
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

    permission_dict = {
        "name": permission.change_display_string(), "display": permission.display_string(),
        "change_type": permission.change_type, "actors": permission.get_actors(),
        "roles": permission.get_roles(), "anyone": permission.anyone,
        "fields": permission.get_configuration(), "pk": permission.pk,
        "change_field_options": permission.get_change_fields(),
        "dependent_field_options": permission.get_all_context_keys()
    }

    if permission.has_condition():
        condition_data = permission.get_condition_data(info="basic")
        condition_data["fields"] = permission.get_condition_data(info="fields")
    else:
        condition_data = None
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


############################
### Standard Django CBVs ###
############################


class GroupListView(LoginRequiredMixin, generic.ListView):
    model = Group
    template_name = 'groups/groups/group_list.html'


class GroupCreateView(LoginRequiredMixin, generic.edit.CreateView):
    model = Group
    template_name = 'groups/groups/group_create.html'
    fields = ['name', 'group_description', 'governing_permission_enabled',
              'foundational_permission_enabled']

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.roles.initialize_with_creator(creator=self.request.user.pk)
        self.object.save()
        return HttpResponseRedirect(reverse('group_detail', kwargs={'pk': self.object.pk}))


class GroupDetailView(LoginRequiredMixin, generic.DetailView):
    model = Group
    template_name = 'groups/groups/group_detail.html'

    def add_user_data_to_context(self, context):

        # Governance info
        context['owners'] = self.client.Community.target.roles.get_owners()
        context['governors'] = self.client.Community.target.roles.get_governors()
        context['governance_info'] = json.dumps(self.client.Community.get_governance_info_as_text())
        context['owner_condition'] = json.dumps(self.client.Community.get_condition_data(leadership_type="owner"))
        context['governor_condition'] = json.dumps(self.client.Community.get_condition_data(leadership_type="governor"))

        # Role/Member info
        context['username_map'] = {person.pk: person.username for person in User.objects.all()}
        context['current_members'] = [member.pk for member in self.client.Community.get_members()]
        user_set = set(context['username_map'].keys())
        member_set = set(context['current_members'])
        context['potential_members'] = list(user_set.difference(member_set))

        # Role Info
        context['roles'] = [
            {'name': role_name, 'current_members': role_data}
            for role_name, role_data in self.client.Community.get_custom_roles().items()
        ]
        # Added for vuex store
        context["users"] = [{'name': person.username, 'pk': person.pk} for person in User.objects.all()]
        return context

    def add_permission_data_to_context(self, context):
        """  This method gets permission *options* and permission configuration *options*, not the permission
        data itself, which is fetched as needed based on user action.

        (note: this matches format specified in vuex store)
        permission_options: {{ permission_options}},
            // {model_name: [ { value: x , text: x} ], model_name: [ { value: x , text: x}  ]}
        permission_configuration_options: {{ permission_configuration_options}},
            // { fieldname: { display: x, type: x, required: x, value: x, field_name: x}}
        """

        context["permission_options"] = {}
        context["permission_configuration_options"] = {}

        for model_class in [Group, Forum, Post, Comment, PermissionsItem, SimpleList]:

            # get settable permissions given model class
            settable_permissions = self.client.PermissionResource.get_settable_permissions_for_model(model_class)

            # get a list of permission options and save to permission_options under the model name
            model_string = model_class.__name__.lower()
            context["permission_options"][model_string] = []
            for permission in settable_permissions:
                context["permission_options"][model_string].append({
                    "value": permission.get_change_type(),
                    "text": permission.description,
                    "group": permission.section
                })

            # get permission configuration options & save, it's ok if things overwrite because they're the same
            for permission in settable_permissions:
                context["permission_configuration_options"].update({
                    permission.get_change_type(): permission.get_configurable_form_fields()
                })

        # get dependent field options
        context["dependent_field_options"] = json.dumps(get_all_dependent_fields())

        # make everything json
        context["permission_options"] = json.dumps(context["permission_options"])
        context["permission_configuration_options"] = json.dumps(context["permission_configuration_options"])

        return context

    def add_condition_data_to_context(self, context):
        """ This method gets condition *options* and configuration *options*, not data for
        existing conditions. (note: this matches format specified in vuex store)

        condition_options: {{ condition_options }},
            // [ { value: x , text: x } ]
        condition_configuration_options: {{ condition_configuration_options }},
            // { fieldname: { display: x, type: x, required: x, value: x, field_name: x } }
        """

        # Get condition options
        settable_conditions = self.client.Conditional.get_possible_conditions()
        condition_options = [{'value': cond.__name__, 'text': cond.descriptive_name} for cond in settable_conditions]
        context["condition_options"] = json.dumps(condition_options)

        # Create condition configuration
        condition_configuration = {}
        for condition in settable_conditions:
            condition_configuration.update({condition.__name__: condition.get_configurable_fields()})
        context["condition_configuration_options"] = json.dumps(condition_configuration)

        return context

    def add_forum_data_to_context(self, context):
        context['forums'] = serialize_forums_for_vue(self.client.Forum.get_forums_owned_by_target())
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.client = Client(actor=self.request.user, target=self.object)
        context = self.add_user_data_to_context(context)
        context = self.add_permission_data_to_context(context)
        context = self.add_condition_data_to_context(context)
        context = self.add_forum_data_to_context(context)
        return context


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
    client.Community.change_group_description(new_description=group_description)

    return JsonResponse({"group_pk": community.pk})


@login_required
def change_group_name(request):

    request_data = json.loads(request.body.decode('utf-8'))
    group_pk = request_data.get("group_pk")
    new_name = request_data.get("new_name")

    client = Client(actor=request.user)
    target = client.Community.get_community(community_pk=group_pk)
    client.Community.set_target(target=target)

    action, result = client.Community.change_name(new_name=new_name)
    action_dict = get_action_dict(action)
    action_dict["group_name"] = new_name
    return JsonResponse(action_dict)


@login_required
def change_group_description(request):

    request_data = json.loads(request.body.decode('utf-8'))
    group_pk = request_data.get("group_pk")
    new_description = request_data.get("new_description")

    client = Client(actor=request.user)
    target = client.Community.get_community(community_pk=group_pk)
    client.Community.set_target(target=target)

    action, result = client.Community.change_group_description(new_description=new_description)
    action_dict = get_action_dict(action)
    action_dict["group_description"] = new_description
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

    action, result = client.Forum.create_forum(name=name, description=description)

    action_dict = get_action_dict(action)
    if action.status == "implemented":
        action_dict["forum_data"] = serialize_forum_for_vue(result)
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
        action_dict["forum_data"] = serialize_forum_for_vue(result)
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

    action, result = client.Forum.add_post(title, content)

    action_dict = get_action_dict(action)
    if action.status == "implemented":
        action_dict["post_data"] = serialize_post_for_vue(result)
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

    action, result = client.Forum.edit_post(title, content)

    action_dict = get_action_dict(action)
    if action.status == "implemented":
        action_dict["post_data"] = serialize_post_for_vue(result)
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

    action, result = client.Community.add_role(role_name=request_data['role_name'])

    return JsonResponse(get_action_dict(action))


@login_required
def remove_role(request, target):

    request_data = json.loads(request.body.decode('utf-8'))

    client = Client(actor=request.user)
    target = client.Community.get_community(community_pk=target)
    client.update_target_on_all(target=target)

    action, result = client.Community.remove_role(role_name=request_data['role_name'])

    return JsonResponse(get_action_dict(action))


@login_required
def add_members(request, target):

    request_data = json.loads(request.body.decode('utf-8'))

    client = Client(actor=request.user)
    target = client.Community.get_community(community_pk=target)
    client.update_target_on_all(target=target)

    action, result = client.Community.add_members(member_pk_list=request_data["user_pks"])

    return JsonResponse(get_action_dict(action))


@login_required
def remove_members(request, target):

    request_data = json.loads(request.body.decode('utf-8'))

    client = Client(actor=request.user)
    target = client.Community.get_community(community_pk=target)
    client.update_target_on_all(target=target)

    action, result = client.Community.remove_members(request_data['user_pks'])

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


def get_permissions_given_role(actor, target, role_name):

    client = Client(actor=actor, target=target)

    existing_permissions = client.PermissionResource.get_permissions_associated_with_role_for_target(role_name=role_name)

    permission_pks, permissions = [], {}
    for permission in existing_permissions:
        permission_pks.append(permission.pk)
        permissions.update(serialize_existing_permission_for_vue(permission))

    return permission_pks, permissions


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
                   permission_roles=None, permission_configuration=None, item_id=None,
                   item_model=None):

    if item_or_role == "item":    # If an item has been passed in, make it the target
        model_class = get_model(item_model)
        target = model_class.objects.get(pk=item_id)
    if item_or_role == "role":    # Otherwise the role the community is set on is the target
        target = Client(actor=request.user).Community.get_community(community_pk=target)

    client = Client(actor=request.user, target=target)

    action, result = client.PermissionResource.add_permission(
        permission_type=permission_type, permission_actors=permission_actors,
        permission_roles=permission_roles, permission_configuration=permission_configuration
    )

    action_dict = get_action_dict(action)
    permission_info = get_permission_info(result) if action.status == "implemented" else None
    action_dict.update({"permission": permission_info, "item_id": item_id, "item_model": item_model})
    return JsonResponse(action_dict)


@login_required
@reformat_input_data
def update_permission(request, target, permission_id, permission_actors=None, permission_roles=None,
                      permission_configuration=None):

    client = Client(actor=request.user)
    target_permission = client.PermissionResource.get_permission(pk=permission_id)

    actions = client.PermissionResource.update_configuration(
        configuration_dict=permission_configuration, permission=target_permission
    )

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
        client.PermissionResource.set_target(target)

        action, result = client.PermissionResource.add_condition_to_permission(
            condition_type=condition_type, condition_data=condition_data, permission_data=permission_data)
        if action.status == "implemented":
            condition_data = result.get_condition_data(info="all")

    elif permission_or_leadership == "leadership":

        target = client.Community.get_community(community_pk=target)
        client.Community.set_target(target)

        action, result = client.Community.add_leadership_condition(
            condition_type=condition_type, leadership_type=leadership_type,
            condition_data=condition_data, permission_data=permission_data
        )
        if action.status == "implemented":
            condition_data = target.get_condition_data(leadership_type=leadership_type, info="all")

    action_dict = get_action_dict(action)
    action_dict.update({
        "condition_info": condition_data, "permission_or_leadership": permission_or_leadership,
        "leadership_type": leadership_type, "target_permission_id": target_permission_id
    })
    return JsonResponse(action_dict)


@login_required
@reformat_input_data
def remove_condition(request, target, permission_or_leadership, target_permission_id=None, leadership_type=None):

    client = Client(actor=request.user)

    if permission_or_leadership == "permission":
        target = client.PermissionResource.get_permission(pk=target_permission_id)
        client.update_target_on_all(target)
        action, result = client.PermissionResource.remove_condition_from_permission()
    elif permission_or_leadership == "leadership":
        target = client.Community.get_community(community_pk=target)
        client.update_target_on_all(target)
        action, result = client.Community.remove_leadership_condition(leadership_type=leadership_type)

    action_dict = get_action_dict(action)
    action_dict.update({
        "permission_or_leadership": permission_or_leadership, "leadership_type": leadership_type,
        "target_permission_id": target_permission_id
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

    return JsonResponse({"permission_data": serialize_existing_permission_for_vue(permission)})


@login_required
def get_permissions(request):

    request_data = json.loads(request.body.decode('utf-8'))

    item_id = request_data.get("item_id")
    model_class = get_model(request_data.get("item_model"))
    target = model_class.objects.get(pk=item_id)

    client = Client(actor=request.user, target=target)
    existing_permissions = client.PermissionResource.get_all_permissions()

    permission_pks, permissions = [], {}
    for permission in existing_permissions:
        permission_pks.append(permission.pk)
        permissions.update(serialize_existing_permission_for_vue(permission))

    return JsonResponse({
        "item_id": item_id, "item_model": request_data.get("item_model"), "permissions": permissions,
        "permission_pks": permission_pks, "foundational": target.foundational_permission_enabled,
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


def serialize_template_for_vue(template, pk_as_key=True):
    template_dict = {
        "pk": template.pk,
        "name": template.name,
        "description": template.user_description,
        "supplied_fields": template.get_supplied_form_fields(),
        "action_breakdown": template.get_template_breakdown()
    }
    if pk_as_key:
        return {template.pk: template_dict}
    return template_dict


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

    action, result = client.List.add_row(row_content=row_content, index=index)

    return JsonResponse(get_action_dict(action))


@login_required
@reformat_input_data
def edit_row(request, target, list_pk, row_content, index):

    client = Client(actor=request.user)
    target = client.List.get_list(pk=list_pk)
    client.List.set_target(target=target)

    action, result = client.List.edit_row(row_content=row_content, index=index)

    return JsonResponse(get_action_dict(action))


@login_required
@reformat_input_data
def move_row(request, target, list_pk, old_index, new_index):

    client = Client(actor=request.user)
    target = client.List.get_list(pk=list_pk)
    client.List.set_target(target=target)

    action, result = client.List.move_row(old_index=old_index, new_index=new_index)

    return JsonResponse(get_action_dict(action))


@login_required
@reformat_input_data
def delete_row(request, target, list_pk, index):

    client = Client(actor=request.user)
    target = client.List.get_list(pk=list_pk)
    client.List.set_target(target=target)

    action, result = client.List.delete_row(index=index)

    return JsonResponse(get_action_dict(action))


##############################
### Permission Check Views ###
##############################


def check_individual_permission(client, actor, permission_name, params):
    """Function which matches a permission name to the actual backend call to be performed,
    returns a lambda function to be executed by caller."""

    group_members = client.Community.target.roles.get_users_given_role("members")
    test_user = User.objects.first() if User.objects.first().pk != actor.pk else User.objects.last()

    # create new client with new target if target is not community
    alt_target = params.pop("alt_target", None) if params else None
    if alt_target:
        model, pk = alt_target.split("_")
        if model == "action":
            """Action is not a PermissionedModel but rarely gets set as target (through
            comments mostly), we automatically give people access to Action comments"""
            return True
        target = client.Action.get_object_given_model_and_pk(model, int(pk))
        client.update_target_on_all(target)

    # Membership
    if permission_name == "add_members":
        return client.PermissionResource.has_permission(
            client.Community, "add_members", {"member_pk_list": [test_user.pk]})
    if permission_name == "remove_members":
        return client.PermissionResource.has_permission(
            client.Community, "remove_members", {"member_pk_list": [test_user.pk]})
    if permission_name == "join_group":
        group_members = client.Community.target.roles.get_users_given_role("members")
        return False if actor.pk in group_members else client.PermissionResource.has_permission(
            client.Community, "add_members", {"member_pk_list": [actor.pk]})
    if permission_name == "leave_group":
        group_members = client.Community.target.roles.get_users_given_role("members")
        return True if actor.pk in group_members else client.PermissionResource.has_permission(
            client.Community, "remove_members", {"member_pk_list": [actor.pk]})
    # Forums & Posts
    if permission_name == "add_forum":
        return client.PermissionResource.has_permission(
            client.Forum, "create_forum", {'name': 'ABC', 'description': 'DEF'})
    if permission_name == "edit_forum":
        return client.PermissionResource.has_permission(
            client.Forum, "edit_forum", {'name': 'ABC', 'description': 'DEF'})
    if permission_name == "delete_forum":
        return client.PermissionResource.has_permission(client.Forum, "delete_forum", {})
    if permission_name == "add_post":
        return client.PermissionResource.has_permission(
            client.Forum, "add_post", {'title': 'ABC', 'content': 'DEF'})
    if permission_name == "edit_post":
        return client.PermissionResource.has_permission(
            client.Forum, "edit_post", {'title': 'ABC', 'content': 'DEF'})
    if permission_name == "delete_post":
        return client.PermissionResource.has_permission(client.Forum, "delete_post", {})
    # Roles
    if permission_name == "add_role":
        return client.PermissionResource.has_permission(client.Community, "add_role", {'role_name': 'ABC'})
    if permission_name == "add_people_to_role":
        return client.PermissionResource.has_permission(
            client.Community, "add_people_to_role", {'role_name': 'ABC', 'people_to_add': [test_user.pk]})
    if permission_name == "remove_people_from_role":
        return client.PermissionResource.has_permission(
            client.Community, "remove_people_from_role", {'role_name': 'ABC', 'people_to_remove': [[test_user.pk]]})
    # Permissions & Conditions
    if permission_name == "add_permission":
        return client.PermissionResource.has_permission(
            client.PermissionResource, "add_permission",
            {"permission_type": 'concord.communities.state_changes.AddMembersStateChange', "anyone": True})
    if permission_name == "remove_permission":
        return client.PermissionResource.has_permission(
            client.PermissionResource, "remove_permission", {})
    if permission_name == "add_actor_to_permission":
        return client.PermissionResource.has_permission(
            client.PermissionResource, "add_actor_to_permission", {"actor": str(test_user.pk)})
    if permission_name == "remove_actor_from_permission":
        return client.PermissionResource.has_permission(
            client.PermissionResource, "remove_actor_from_permission", {"actor": str(test_user.pk)})
    if permission_name == "add_role_to_permission":
        return client.PermissionResource.has_permission(
            client.PermissionResource, "add_role_to_permission", {"role_name": "fakerole"})
    if permission_name == "remove_role_from_permission":
        return client.PermissionResource.has_permission(
            client.PermissionResource, "remove_role_from_permission", {"role_name": "fakerole"})
    if permission_name == "give_anyone_permission":
        return client.PermissionResource.has_permission(
            client.PermissionResource, "give_anyone_permission", {})
    if permission_name == "remove_anyone_from_permission":
        return client.PermissionResource.has_permission(
            client.PermissionResource, "remove_anyone_from_permission", {})
    if permission_name == "change_configuration_of_permission":
        return client.PermissionResource.has_permission(
            client.PermissionResource, "change_configuration_of_permission",
            {"configurable_field_name": "ABC", "configurable_field_value": "DEF"})
    if permission_name == "add_condition_to_permission":
        return client.PermissionResource.has_permission(
            client.PermissionResource, "add_condition_to_permission", {"condition_type": "ApprovalCondition"})
    if permission_name == "remove_condition_from_permission":
        return client.PermissionResource.has_permission(
            client.PermissionResource, "remove_condition_from_permission", {})
    if permission_name == "add_leadership_condition":
        return client.PermissionResource.has_permission(
            client.Community, "add_leadership_condition",
            {"leadership_type": params["leadership_type"], "condition_type": "ApprovalCondition"})
    if permission_name == "remove_leadership_condition":
        return client.PermissionResource.has_permission(
            client.Community, "remove_leadership_condition", {"leadership_type": params["leadership_type"]})
    if permission_name == "enable_foundational_permission":
        return client.PermissionResource.has_permission(client.Action, "enable_foundational_permission", {})
    if permission_name == "disable_foundational_permission":
        return client.PermissionResource.has_permission(client.Action, "disable_foundational_permission", {})
    if permission_name == "enable_governing_permission":
        return client.PermissionResource.has_permission(client.Action, "enable_governing_permission", {})
    if permission_name == "disable_governing_permission":
        return client.PermissionResource.has_permission(client.Action, "disable_governing_permission", {})
    # leaders
    if permission_name == "update_owners":
        if client.PermissionResource.has_permission(client.Community, "add_owner", {"owner_pk": [test_user.pk]}):
            return True
        if client.PermissionResource.has_permission(client.Community, "remove_owner", {"owner_pk": [test_user.pk]}):
            return True
        if client.PermissionResource.has_permission(client.Community, "add_owner_role", {"owner_role": "ABC"}):
            return True
        if client.PermissionResource.has_permission(client.Community, "remove_owner_role", {"owner_role": "ABC"}):
            return True
        return False
    if permission_name == "update_governors":
        if client.PermissionResource.has_permission(client.Community, "add_governor", {"governor_pk": [test_user.pk]}):
            return True
        if client.PermissionResource.has_permission(client.Community, "remove_governor", {"governor_pk": [test_user.pk]}):
            return True
        if client.PermissionResource.has_permission(client.Community, "add_governor_role", {"governor_role": "ABC"}):
            return True
        if client.PermissionResource.has_permission(client.Community, "remove_governor_role", {"governor_role": "ABC"}):
            return True
        return False
    # templates
    if permission_name == "apply_template":
        return client.PermissionResource.has_permission(
            client.Template, "apply_template", {"template_model_pk": TemplateModel.objects.first().pk})
    # comments
    if permission_name == "add_comment":
        return client.PermissionResource.has_permission(client.Comment, "add_comment", {"text": "ABC"})
    if permission_name == "edit_comment":
        return client.PermissionResource.has_permission(client.Comment, "edit_comment", {"text": "DEF"})
    if permission_name == "delete_comment":
        return client.PermissionResource.has_permission(client.Comment, "delete_comment", {})
    # lists
    if permission_name == "add_list":
        return client.PermissionResource.has_permission(
            client.List, "add_list", {"name": "ABC", "configuration": {"content": {"required": True}}})
    if permission_name == "edit_list":
        return client.PermissionResource.has_permission(client.List, "edit_list", {"name": "DEF"})
    if permission_name == "delete_list":
        return client.PermissionResource.has_permission(client.List, "delete_list", {})
    if permission_name == "add_row":
        return client.PermissionResource.has_permission(client.List, "add_row", {"row_content": "ABC"})
    if permission_name == "edit_row":
        return client.PermissionResource.has_permission(client.List, "edit_row", {"row_content": "ABC", "index": 0})
    if permission_name == "move_row":
        return client.PermissionResource.has_permission(client.List, "move_row", {"old_index": 0, "new_index": 0})
    if permission_name == "delete_row":
        return client.PermissionResource.has_permission(client.List, "delete_row", {"index": 0})

    logger.warn(f"no permission {permission_name} found")
    return False


@reformat_input_data
@login_required
def check_permissions(request, target, permissions):
    """Given a list of zero or more permission names, gets the function call to check if we have
    that permission and calls it.  Returns a list of permissions with boolean values indicating
    whether or not the use has the permissions."""

    client = Client(actor=request.user)
    target = client.Community.get_community(community_pk=target)
    client.update_target_on_all(target=target)

    permission_dict = {}
    for permission_name, params in permissions.items():
        client.update_target_on_all(target=target)  # reset target if it was edited for last permission
        has_permission = check_individual_permission(client, request.user, permission_name, params)
        permission_dict.update({permission_name: has_permission})

    return JsonResponse({"user_permissions": permission_dict})
