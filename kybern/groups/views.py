from django.views import generic
from django.http import HttpResponseRedirect, JsonResponse
import json

from django.urls import reverse
from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required


from concord.actions.client import ActionClient
from concord.communities.client import CommunityClient
from concord.permission_resources.client import PermissionResourceClient
from concord.conditionals.client import PermissionConditionalClient, CommunityConditionalClient
from concord.resources.client import CommentClient
from concord.resources.models import Comment

from accounts.models import User
from .models import Group, Forum, Post
from .client import ForumClient



##################################
### Helper methods and classes ###
##################################


# FIXME: this probably doesn't belong here
class GroupClient(CommunityClient):
    """Easy way to replace the default community model with the one we want to use here, group."""
    community_model = Group


def get_model(model_name):
    for app_config in apps.get_app_configs():
        try:
            model = app_config.get_model(model_name)
            return model
        except LookupError:
            pass


def process_action(action):

    if action.resolution.status == "implemented":
        action_verb = ""
        action_description = action.change.description_past_tense() + " " + action.target.get_name()
        follow_up = "They did so because they have the permission %s." % action.resolution.resolved_through
    else:
        action_verb = "tried to "
        action_description = action.change.description_present_tense() + " " + action.target.get_name()
        follow_up = "The current status is weird, do something here."

    action_string = "At %s, %s %s%s. %s" % (action.created_at.strftime("%b %d %Y %I:%M%p"), 
        action.actor.username, action_verb, action_description, follow_up)

    # Check for condition  ( FIXME: we need a much more performant way of doing this )
    pcc = PermissionConditionalClient(actor="system")
    condition = pcc.get_condition_item_given_action(action_pk=action.pk)

    return {
        "action_pk": action.pk,
        "action_target_pk": action.object_id,
        "action_target_model": action.target.__class__.__name__,   # will this work???
        "action_target_content_type": action.content_type.pk,
        "description": action.get_description(),
        "created": str(action.created_at),
        "display_date": action.created_at.strftime("%b %d %Y %I:%M%p"),
        "actor": action.actor.username,
        "status": action.resolution.status,
        "resolution passed by": action.resolution.resolved_through,
        "display": action_string,
        "has_condition": {
            "exists": True if condition else False,
            "pk": condition.pk if condition else None,
            "type": condition.__class__.__name__ if condition else None,
            "status": condition.condition_status() if condition else None
        }
    }


def get_action_dict(action):
    action_log = action.resolution.log
    if (not action_log and action.resolution.status == "waiting"):
        action_log = "waiting on condition"
    return { 
        "action_created": True if action.resolution.status in ["implemented", "approved", "waiting", "rejected"] else False,
        "action_status": action.resolution.status,
        "action_log": action_log,
        "action_pk": action.pk,
    }


def get_multiple_action_dicts(actions):
    # overall data
    action_log = ""
    action_status = "implemented"
    for action in actions:
        if action.resolution.status != "implemented":
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


def serialize_existing_permission_for_vue(permission):
    """  (note: this matches format specified in vuex store)
    permissions: {{ permissions }},         
        // { int(pk) : { name: x, display: x, change_type: x } } """
    return { permission.pk : { "name": permission.full_description(), "display": permission.full_description(), 
            "change_type": permission.change_type, "actors": permission.get_actors(), "roles": permission.get_role_names() } }


def serialize_existing_permission_configuration_for_vue(permission):
    """  (note: this matches format specified in vuex store)
    permission_configurations: {{ permission_configurations }},
        // { int(pk) : { permissionfieldname : permissionfieldvalue } }       
    """
    return { permission.pk: permission.get_configuration() } 


def serialize_existing_condition_for_vue(condition):
    """ (note: this matches format specified in vuex store)
    conditions: {{ conditions }},         
        // { int(pk) : { name: x, display: x, conditioned_object_pk: x } }       
    """
    return { condition.pk :  { 'name' : condition.condition_name(), 'display': condition.condition_description(), 
        'conditioned_object_pk': condition.conditioned_object_id } }


def serialize_existing_condition_configuration_for_vue(condition):
    """ (note: this matches format specified in vuex store)
    condition_configurations: {{ condition_configurations }},
        // { int(pk) : { conditionfieldname : conditionfieldvalue } }       
    """
    return { condition.pk: condition.condition_data.get_configurable_fields_with_data() }


def serialize_existing_comment_for_vue(comment):
    """ Serializes comment from Django model to JSOn-serializable dict.
    (note: this matches format specified in vuex store)    
    """
    return { comment.pk: { 'pk': comment.pk, 'text': comment.text, 'commentor_pk': comment.commentor.pk, 
        'created_at': comment.created_at, 'updated_at': comment.updated_at } }


def serialize_forum_for_vue(forum):
    return { 'pk': forum.pk, 'name': forum.name, 'description': forum.description }


def serialize_post_for_vue(post):
    return { 'pk': post.pk, 'title': post.title, 'content': post.content, 'forum_pk': post.forum.pk, 
        'created': post.created, 'author': post.author.pk }


def serialize_forums_for_vue(forums):

    forum_list = []
    for forum in forums:
        forum_list.append(serialize_forum_for_vue(forum))

    return forum_list


############################
### Standard Django CBVs ###
############################


class GroupListView(LoginRequiredMixin, generic.ListView):
    model = Group
    template_name = 'groups/group_list.html'


class GroupCreateView(LoginRequiredMixin, generic.edit.CreateView):
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


class GroupDetailView(LoginRequiredMixin, generic.DetailView):
    model = Group
    template_name = 'groups/group_detail.html'

    def prep_clients(self):
        self.communityClient = GroupClient(actor=self.request.user, target=self.object)
        self.permissionClient = PermissionResourceClient(actor=self.request.user, target=self.object)
        self.actionClient = ActionClient(actor=self.request.user, target=self.object)
        self.conditionalClient = PermissionConditionalClient(actor=self.request.user)
        self.leadershipConditionalClient = CommunityConditionalClient(actor=self.request.user, target=self.object)
        self.forumClient = ForumClient(actor=self.request.user, target=self.object)

    def add_user_data_to_context(self, context):

        # Governance info
        context['owners'] = self.communityClient.target.roles.get_owners()
        context['governors'] = self.communityClient.target.roles.get_governors()
        context['governance_info'] = json.dumps(self.communityClient.get_governance_info_as_text())

        owner_condition = self.leadershipConditionalClient.get_condition_template_for_owner()
        governor_condition = self.leadershipConditionalClient.get_condition_template_for_governor()
        context['owner_condition_pk'] = json.dumps(owner_condition.pk if owner_condition else None)
        context['governor_condition_pk'] = json.dumps(governor_condition.pk if governor_condition else None)
        
        # Role/Member info
        context['username_map'] = { person.pk : person.username for person in User.objects.all() }
        context['current_members'] = [member.pk for member in self.communityClient.get_members()]
        context['potential_members'] = list(set(context['username_map'].keys()).difference(set(context['current_members'])))
        
        # Role Info
        context['roles'] = [ { 'name': role_name, 'current_members': role_data } 
                                        for role_name, role_data in self.communityClient.get_custom_roles().items() ]
        # Added for vuex store
        context["users"] = [ { 'name' : person.username, 'pk': person.pk } for person in User.objects.all() ]
        return context

    def add_permission_data_to_context(self, context):
        """  This method gets permission *options* and permission configuration *options*, not the permission
        data itself, which is fetched as needed based on user action.  
        
        (note: this matches format specified in vuex store)     
        permission_options: {{ permission_options }},
            // { model_name: [ { value: x , text: x } ], model_name: [ { value: x , text: x } ] }
        permission_configuration_options: {{ permission_configuration_options }},
            // { fieldname: { display: x, type: x, required: x, value: x, field_name: x } }
        """

        context["permission_options"] = {}
        context["permission_configuration_options"] = {}

        for model_class in [Group, Forum, Post, Comment]:

            # get settable permissions given model class
            settable_permissions = self.permissionClient.get_settable_permissions_for_model(model_class)

            # get a list of permission options and save to permission_options under the model name
            model_string = model_class.__name__.lower()
            context["permission_options"][model_string] = []
            for permission in settable_permissions:
                context["permission_options"][model_string].append({ "value": permission.get_change_type(), 
                    "text": permission.description })

            # get permission configuration options & save, it's ok if things overwrite because they're the same
            for permission in settable_permissions:
                context["permission_configuration_options"].update({
                    permission.get_change_type(): permission.get_configurable_form_fields()
                })            
            
        # make everything json
        context["permission_options"] = json.dumps(context["permission_options"])
        context["permission_configuration_options"] = json.dumps(context["permission_configuration_options"])

        return context

    def add_condition_data_to_context(self, context):
        """ This method gets condition *options* and configuration *options*, not data for existing conditions.
        
        (note: this matches format specified in vuex store)
        condition_options: {{ condition_options }},
            // [ { value: x , text: x } ]
        condition_configuration_options: {{ condition_configuration_options }},
            // { fieldname: { display: x, type: x, required: x, value: x, field_name: x } }   
        TODO: make format below align with this documentation (which corresponds to what vue expects)      
        """

        # Get condition options
        settable_conditions = self.conditionalClient.get_possible_conditions()
        condition_options = [ { 'value': cond.__name__, 'text': cond.descriptive_name } for cond in settable_conditions ]
        context["condition_options"] = json.dumps(condition_options)

        # Create condition configuration 
        condition_configuration = { }
        for condition in settable_conditions:
            condition_configuration.update({ condition.__name__ : condition.get_configurable_fields() })
        context["condition_configuration_options"] = json.dumps(condition_configuration)

        # Get & serialize existing conditions
        owner_condition = self.leadershipConditionalClient.get_condition_template_for_owner()
        governor_condition = self.leadershipConditionalClient.get_condition_template_for_governor()
        serialized_conditions = {}
        for condition in [owner_condition, governor_condition]:
            if condition:
                serialized_conditions.update(serialize_existing_condition_for_vue(condition))
        context["conditions"] = json.dumps(serialized_conditions)

        # Get & serialize existing condition configurations
        serialized_condition_configurations = {}
        for condition in [owner_condition, governor_condition]:
            if condition:
                serialized_condition_configurations.update(serialize_existing_condition_configuration_for_vue(condition))
        context["condition_configurations"] = json.dumps(serialized_condition_configurations)

        return context

    def add_forum_data_to_context(self, context):
        context['forums'] = serialize_forums_for_vue(self.forumClient.get_forums_owned_by_target())
        return context

    def get_context_data(self, **kwargs):
        # TODO: refactor this into stuff returned from API calls (or at least view mixins)
        context = super().get_context_data(**kwargs)
        self.prep_clients()
        context = self.add_user_data_to_context(context)
        context = self.add_permission_data_to_context(context)
        context = self.add_condition_data_to_context(context)
        context = self.add_forum_data_to_context(context)
        context["base_url"] = "http://" + self.request.get_host()   # FIXME: should check for http vs https
        return context        


####################
### Forums Views ###
####################


@login_required
def get_forums(request, target):
    communityClient = GroupClient(actor=request.user)
    target = communityClient.get_community(community_pk=target)
    communityClient.set_target(target=target)

    forumClient = ForumClient(actor=request.user, target=target)

    forums = forumClient.get_forums_owned_by_target()
    forum_list = serialize_forums_for_vue(forums)

    return JsonResponse({ "forums": forum_list })


@login_required
def add_forum(request, target):

    communityClient = GroupClient(actor=request.user)
    target = communityClient.get_community(community_pk=target)
    communityClient.set_target(target=target)

    request_data = json.loads(request.body.decode('utf-8'))
    name = request_data.get("name")
    description = request_data.get("description", None)

    forumClient = ForumClient(actor=request.user, target=target)
    action, result = forumClient.create_forum(name=name, description=description)
    
    action_dict = get_action_dict(action)
    action_dict["forum_data"] = serialize_forum_for_vue(result)
    return JsonResponse(action_dict)


@login_required
def edit_forum(request, target):
    
    request_data = json.loads(request.body.decode('utf-8'))
    pk = request_data.get("pk")
    name = request_data.get("name", None)
    description = request_data.get("description", None)

    forumClient = ForumClient(actor=request.user)
    forum = forumClient.get_forum_given_pk(pk)
    forumClient.set_target(target=forum)

    action, result = forumClient.edit_forum(pk=pk, name=name, description=description)

    action_dict = get_action_dict(action)
    if action.resolution.status == "implemented":
        action_dict["forum_data"] = serialize_forum_for_vue(result)
    return JsonResponse(action_dict)


@login_required
def delete_forum(request, target):

    request_data = json.loads(request.body.decode('utf-8'))
    pk = request_data.get("pk")

    forumClient = ForumClient(actor=request.user)
    forum = forumClient.get_forum_given_pk(pk)
    forumClient.set_target(target=forum)

    action, result = forumClient.delete_forum(pk=pk)

    action_dict = get_action_dict(action)
    action_dict["deleted_forum_pk"] = pk
    return JsonResponse(action_dict)


@login_required
def get_posts_for_forum(request, target):

    request_data = json.loads(request.body.decode('utf-8'))
    forum_pk = request_data.get("forum_pk")

    forumClient = ForumClient(actor=request.user)
    forum = forumClient.get_forum_given_pk(forum_pk)
    forumClient.set_target(target=forum)
    posts = forumClient.get_posts_for_forum()

    serialized_posts = [serialize_post_for_vue(post) for post in posts]

    return JsonResponse({ 'forum_pk': forum_pk, 'posts': serialized_posts })


@login_required
def add_post(request, target):

    request_data = json.loads(request.body.decode('utf-8'))
    forum_pk = request_data.get("forum_pk")
    title = request_data.get("title")
    content = request_data.get("content", None)

    forumClient = ForumClient(actor=request.user)
    forum = forumClient.get_forum_given_pk(forum_pk)
    forumClient.set_target(target=forum)

    action, result = forumClient.add_post(forum_pk, title, content)
    
    action_dict = get_action_dict(action)
    action_dict["post_data"] = serialize_post_for_vue(result)
    return JsonResponse(action_dict)


@login_required
def edit_post(request, target):

    request_data = json.loads(request.body.decode('utf-8'))
    pk = request_data.get("pk")
    title = request_data.get("title", None)
    content = request_data.get("content", None)

    forumClient = ForumClient(actor=request.user)
    post = forumClient.get_post_given_pk(pk)
    forumClient.set_target(target=post)

    action, result = forumClient.edit_post(pk, title, content)

    action_dict = get_action_dict(action)
    if action.resolution.status == "implemented":
        action_dict["post_data"] = serialize_post_for_vue(result)
    return JsonResponse(action_dict)


@login_required
def delete_post(request, target):

    request_data = json.loads(request.body.decode('utf-8'))
    pk = request_data.get("pk")
    forum_pk = request_data.get("forum_pk")

    forumClient = ForumClient(actor=request.user)
    forum = forumClient.get_forum_given_pk(forum_pk)
    forumClient.set_target(target=forum)

    action, result = forumClient.delete_post(pk=pk)

    action_dict = get_action_dict(action)
    action_dict["deleted_post_pk"] = pk
    print(action_dict)
    return JsonResponse(action_dict)
    


################################################################################
### Helper methods, likely to be moved to concord, called by vuex data store ###
################################################################################


@login_required
def add_role(request, target):

    request_data = json.loads(request.body.decode('utf-8'))

    communityClient = GroupClient(actor=request.user)
    target = communityClient.get_community(community_pk=target)
    communityClient.set_target(target=target)
    
    action, result = communityClient.add_role(role_name=request_data['role_name'])
    
    return JsonResponse(get_action_dict(action))


@login_required
def add_members(request, target):

    request_data = json.loads(request.body.decode('utf-8'))

    communityClient = GroupClient(actor=request.user)
    target = communityClient.get_community(community_pk=target)
    communityClient.set_target(target=target)

    action, result = communityClient.add_members(member_pk_list=request_data["user_pks"])

    return JsonResponse(get_action_dict(action))


@login_required
def remove_members(request, target):

    request_data = json.loads(request.body.decode('utf-8'))

    communityClient = GroupClient(actor=request.user)
    target = communityClient.get_community(community_pk=target)
    communityClient.set_target(target=target)

    action, result = communityClient.remove_members(request_data['user_pks'])

    return JsonResponse(get_action_dict(action))


@login_required
def add_people_to_role(request, target):

    request_data = json.loads(request.body.decode('utf-8'))

    communityClient = GroupClient(actor=request.user)
    target = communityClient.get_community(community_pk=target)
    communityClient.set_target(target=target)

    action, result = communityClient.add_people_to_role(role_name=request_data['role_name'], 
        people_to_add=request_data['user_pks'])

    return JsonResponse(get_action_dict(action))


@login_required
def remove_people_from_role(request, target):

    request_data = json.loads(request.body.decode('utf-8'))

    communityClient = GroupClient(actor=request.user)
    target = communityClient.get_community(community_pk=target)
    communityClient.set_target(target=target)

    action, result = communityClient.remove_people_from_role(role_name=request_data['role_name'], 
        people_to_remove=request_data['user_pks'])

    return JsonResponse(get_action_dict(action))


####################################
### Condition & permission views ###
####################################


def get_permissions_given_role(actor, target, role_name):

    # get permissions
    existing_permissions = PermissionResourceClient(actor=actor, target=target).\
        get_permissions_associated_with_role_for_target(role_name=role_name)

    permission_pks, permissions, permission_configurations = [], {}, {}
    for permission in existing_permissions:
        permission_pks.append(permission.pk)
        permissions.update(serialize_existing_permission_for_vue(permission))
        permission_configurations.update(serialize_existing_permission_configuration_for_vue(permission))
        
    return permission_pks, permissions, permission_configurations


def get_conditions_given_role(actor, target, role_name):

    # get permissions & the associated conditions
    existing_permissions = PermissionResourceClient(actor=actor, target=target).\
        get_permissions_for_role(role_name=role_name)
    conditionalClient = PermissionConditionalClient(actor=actor)
    existing_conditions = conditionalClient.get_conditions_given_targets(
            target_pks=[permission.pk for permission in existing_permissions])

    conditions, condition_configurations = {}, {}
    for condition in existing_conditions:
        conditions.update(serialize_existing_condition_for_vue(condition))
        condition_configurations.update(serialize_existing_condition_configuration_for_vue(condition))

    return conditions, condition_configurations


@login_required
def get_data_for_role(request, target):

    actor = request.user
    communityClient = GroupClient(actor=actor)
    target = communityClient.get_community(community_pk=target)
    request_data = json.loads(request.body.decode('utf-8'))
    role_name = request_data['role_name']
    
    permission_pks, permissions, permission_configurations = get_permissions_given_role(actor, target, role_name)
    conditions, condition_configurations = get_conditions_given_role(actor, target, role_name)

    return JsonResponse({ "permissions" : permissions, "permission_configurations" : permission_configurations,
        "conditions" : conditions, "condition_configurations" : condition_configurations,
        "role_permissions": permission_pks })


def reformat_permission_field(field):
    if field["type"] == "PermissionRoleField":
        if "other_data" in field and "multiple" in field["other_data"] and field["other_data"]["multiple"] == False:
            field["value"] = field["value"]["name"]   # Single select treated differently
        else:
            field["value"] = [data["name"] for data in field["value"]] if field["value"] else []
    elif field["type"] == "PermissionActorField":
        try:
            field["value"] = [data["value"] for data in field["value"]] if field["value"] else []
        except:
            # if the above doesn't work, try to get by pk
            field["value"] = [data["pk"] for data in field["value"]] if field["value"] else []
        # make sure individual items in list are ints
        field["value"] = [int(pk) for pk in field["value"]]
    return field


def reformat_permission_data(permission_configuration):
    """
    [{'field_name': 'role_name', 'display': 'Roles people can be added to', 'type': 'PermissionRoleField', 'required': False, 'value': [{'name': 'romans'}]}]

    """
    fields = {}
    for field in permission_configuration:
        field = reformat_permission_field(field)
        fields.update({
            field["field_name"] : field["value"]
        })
    return fields


def process_configuration_data(configuration_data):
    """Splits configuration data into condition_data and permission_data."""
    configuration_data = json.loads(configuration_data) if type(configuration_data) == str else configuration_data
    condition_data = []
    permission_data = []
    for field in configuration_data:
        field = reformat_permission_field(field)
        if field["type"] in ["PermissionRoleField", "PermissionActorField"]:
            permission_data.append(field)
        else:
            condition_data.append(field)
    return condition_data, permission_data


def get_permission_info(permission):
    return {
        "pk": permission.pk,
        "permission_data": list(serialize_existing_permission_for_vue(permission).values()),
        "configuration_data": list(serialize_existing_permission_configuration_for_vue(permission).values())
    }


@login_required
def add_permission(request, target):

    request_data = json.loads(request.body.decode('utf-8'))
    permission_type = request_data.get("permission_type", None)
    permission_actors = request_data.get("permission_actors", None)
    permission_roles = request_data.get("permission_roles", None)
    permission_configuration = request_data.get("permission_configuration", None)

    reformatted_permission_data = reformat_permission_data(permission_configuration)

    communityClient = GroupClient(actor=request.user)
    target = communityClient.get_community(community_pk=target)
    permissionClient = PermissionResourceClient(actor=request.user, target=target)

    action, result = permissionClient.add_permission(permission_type=permission_type, 
        permission_actors=permission_actors, permission_roles=permission_roles, 
        permission_configuration=reformatted_permission_data)

    action_dict = get_action_dict(action)
    permission_info = get_permission_info(result) if action.resolution.status == "implemented" else None
    action_dict.update({ "permission": permission_info })

    return JsonResponse(action_dict)


@login_required
def update_permission(request, target):

    request_data = json.loads(request.body.decode('utf-8'))
    permission_id = request_data.get("permission_id", None)
    permission_configuration = request_data.get("permission_configuration", None)

    actors = request_data.get("actors", None)
    roles = request_data.get("roles", None)

    reformatted_permission_data = reformat_permission_data(permission_configuration)

    permissionClient = PermissionResourceClient(actor=request.user)
    target_permission = permissionClient.get_permission(pk=permission_id)
    permissionClient.set_target(target=target_permission)
    actions = permissionClient.update_configuration(configuration_dict=reformatted_permission_data, 
        permission=target_permission)

    if actors:
        actor_data = [ actor['pk'] for actor in actors]
        actor_actions = permissionClient.update_actors_on_permission(actor_data=actor_data, permission=target_permission)
        actions += actor_actions
    if roles:
        role_data = [ role['name'] for role in roles]
        role_actions = permissionClient.update_roles_on_permission(role_data=role_data, permission=target_permission)
        actions += role_actions

    print(actions)

    action_dict = get_multiple_action_dicts(actions)

    permission = permissionClient.get_permission(pk=permission_id)  # get refreshed version
    permission_info = get_permission_info(permission)
    action_dict.update({ "permission" : permission_info })

    return JsonResponse(action_dict)


@login_required
def delete_permission(request, target):

    request_data = json.loads(request.body.decode('utf-8'))
    permission_id = request_data.get("permission_id", None)

    communityClient = GroupClient(actor=request.user)
    target = communityClient.get_community(community_pk=target)
    permissionClient = PermissionResourceClient(actor=request.user, target=target)
    permission_target = permissionClient.get_permission(pk=permission_id)
    conditionalClient = PermissionConditionalClient(actor=request.user, target=permission_target)

    # try to remove condition
    condition = conditionalClient.get_condition_template()
    if condition:
        action, result = conditionalClient.remove_condition(condition=condition)
        if action.resolution.status != "implemented":
            message = """In order to delete a permission, any conditions set on the permission must first be 
                deleted. The following condition on this permission could not be deleted: %s 
                It could not be deleted because: %s""" % (condition.get_name(), action.resolution.log)
            return JsonResponse({ "action_status": "failure", "action_log" : message })

    # now remove permission
    action, result = permissionClient.remove_permission(item_pk=permission_id)
    action_dict = get_action_dict(action)
    action_dict.update({ "removed_permission_pk": permission_id })
    return JsonResponse(action_dict)


####################################
### Views for setting conditions ###
####################################


def leadership_condition_helper(request, request_data, target, action_type):

    communityClient = GroupClient(actor=request.user)
    target = communityClient.get_community(community_pk=target)
    conditionalClient = CommunityConditionalClient(actor=request.user, target=target)

    called_for = request_data.get("called_for")
    condition_id = request_data.get("condition_id", None)
    condition_type = request_data.get("condition_type", None)
    configuration_data = request_data.get("condition_configuration", None)
    if configuration_data:
        condition_data, permission_data = process_configuration_data(configuration_data)

    if action_type == "add":

        if called_for == "owner":
            return conditionalClient.add_condition_to_owners(condition_data=condition_data,
                permission_data=permission_data, condition_type=condition_type)
        elif called_for == "governor":
            return conditionalClient.add_condition_to_governors(condition_data=condition_data,
                permission_data=permission_data, condition_type=condition_type)

    if action_type == "update":
        return conditionalClient.change_condition(condition_pk=condition_id,
            condition_data=condition_data, permission_data=permission_data)

    if action_type == "delete":
        condition = conditionalClient.get_condition_template()
        return conditionalClient.remove_condition(condition=condition)


def permission_condition_helper(request, request_data, target, action_type):

    target_permission_id = request_data.get("target_permission_id", None)
    target_permission = PermissionResourceClient(actor=request.user).get_permission(pk=target_permission_id)
    conditionalClient = PermissionConditionalClient(actor=request.user, target=target_permission)

    condition_type = request_data.get("condition_type", None)
    condition_id = request_data.get("condition_id", None)
    configuration_data = request_data.get("condition_configuration", None)
    if configuration_data:
        condition_data, permission_data = process_configuration_data(configuration_data)

    if action_type == "add":
        return conditionalClient.add_condition(condition_type=condition_type.lower(),
            condition_data=condition_data, permission_data=permission_data)

    if action_type == "update":
        return conditionalClient.change_condition(condition_pk=condition_id,
            condition_data=condition_data, permission_data=permission_data)

    if action_type == "delete":
        condition = conditionalClient.get_condition_template()
        return conditionalClient.remove_condition(condition=condition)


def get_condition_info(condition):
    return {
        "pk": condition.pk,
        "condition_data": list(serialize_existing_condition_for_vue(condition).values()),
        "configuration_data": list(serialize_existing_condition_configuration_for_vue(condition).values())
    }


@login_required
def manage_condition(request, target):

    request_data = json.loads(request.body.decode('utf-8'))
    target_type = request_data.get("target_type")
    request_type = request_data.get("request_type")

    if target_type == "community":
        action, result = leadership_condition_helper(request, request_data, target, request_type)
    else:
        action, result = permission_condition_helper(request, request_data, target, request_type)

    if request_type in ["add", "update"]:
        condition_info = get_condition_info(result) if action.resolution.status == "implemented" else None
        action_dict = get_action_dict(action)
        action_dict.update({ "condition_info": get_condition_info(result) })
        return JsonResponse(action_dict)

    if request_type == "delete":
        action_dict = get_action_dict(action)
        action_dict.update({ "deleted_condition_pk": request_data.get("condition_id") })
        return JsonResponse(action_dict)


#############################################
### Views for interacting with conditions ###
#############################################


@login_required
def update_approval_condition(request):

    request_data = json.loads(request.body.decode('utf-8'))
    condition_pk = request_data.get("condition_pk", None)
    action_to_take = request_data.get("action_to_take", None)

    conditionalClient = PermissionConditionalClient(actor=request.user)
    approvalClient = conditionalClient.get_approval_condition_as_client(pk=condition_pk)

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

    conditionalClient = PermissionConditionalClient(actor=request.user)
    voteClient = conditionalClient.get_vote_condition_as_client(pk=condition_pk)
    
    action, result = voteClient.vote(vote=action_to_take)

    return JsonResponse(get_action_dict(action))


@login_required
def get_conditional_data(request):

    request_data = json.loads(request.body.decode('utf-8'))
    condition_pk = request_data.get("condition_pk", None)
    condition_type = request_data.get("condition_type", None)

    conditionalClient = PermissionConditionalClient(actor=request.user)
    condition = conditionalClient.get_condition_item(condition_pk=condition_pk, condition_type=condition_type)

    # for permission on condition, does user have permission? 
    permissionClient = PermissionResourceClient(actor=request.user)
    permission_details = {}
    for permission in permissionClient.get_permissions_on_object(object=condition):
        has_permission = permissionClient.actor_satisfies_permission(actor=request.user,
            permission=permission)
        permission_details.update({ permission.change_type : has_permission })
    permission_details.update({ 'user_condition_status': condition.user_condition_status(user=request.user) })

    return JsonResponse({ "permission_details" : permission_details,
        "condition_details" : { 
            "status": condition.condition_status(),
            "display_status": condition.display_status(),
            "fields": condition.display_fields()
        }
    })


@login_required
def get_action_data(request):

    request_data = json.loads(request.body.decode('utf-8'))
    action_pk = request_data.get("action_pk", None)

    action = ActionClient(actor=request.user).get_action_given_pk(action_pk)

    return JsonResponse({ "action_data": process_action(action) })


@login_required
def get_action_data_for_target(request):

    request_data = json.loads(request.body.decode('utf-8'))

    item_id = request_data.get("item_id")
    model_class = get_model(request_data.get("item_model"))
    target = model_class.objects.get(pk=item_id)

    actionClient = ActionClient(actor=request.user, target=target)
    actions = actionClient.get_action_history_given_target()

    return JsonResponse({ "action_data": [process_action(action) for action in actions] })


####################################
### Views for leadership include ###
####################################


@login_required
def update_owners(request, target):

    request_data = json.loads(request.body.decode('utf-8'))
    owner_roles = request_data.get("owner_roles", "")  # no need to make into list, leadershipcomponent handles that
    owner_actors = request_data.get("owner_actors", "")  # no need to make into list, leadershipcomponent handles that

    communityClient = GroupClient(actor=request.user)
    target = communityClient.get_community(community_pk=target)
    communityClient.set_target(target=target)

    actions = communityClient.update_owners(new_owner_data={"individuals": owner_actors, "roles": owner_roles})

    action_dict = get_multiple_action_dicts(actions)
    action_dict.update({ "governance_info": json.dumps(communityClient.get_governance_info_as_text()) })

    return JsonResponse(action_dict)


@login_required
def update_governors(request, target):

    request_data = json.loads(request.body.decode('utf-8'))
    governor_roles = request_data.get("governor_roles", "")  # no need to make into list, leadershipcomponent handles that
    governor_actors = request_data.get("governor_actors", "")  # no need to make into list, leadershipcomponent handles that

    communityClient = GroupClient(actor=request.user)
    target = communityClient.get_community(community_pk=target)
    communityClient.set_target(target=target)

    actions = communityClient.update_governors(new_governor_data={"individuals": governor_actors, "roles": governor_roles})

    action_dict = get_multiple_action_dicts(actions)
    action_dict.update({ "governance_info": json.dumps(communityClient.get_governance_info_as_text()) })

    return JsonResponse(action_dict)


#############################
### Item permission views ###
#############################


@login_required
def get_permissions_and_conditions(request):

    request_data = json.loads(request.body.decode('utf-8'))

    item_id = request_data.get("item_id")
    model_class = get_model(request_data.get("item_model"))
    target = model_class.objects.get(pk=item_id)

    permClient = PermissionResourceClient(actor=request.user, target=target)

    existing_permissions = permClient.get_all_permissions()

    permission_pks, permissions, permission_configurations = [], {}, {}
    for permission in existing_permissions:
        permission_pks.append(permission.pk)
        permissions.update(serialize_existing_permission_for_vue(permission))
        permission_configurations.update(serialize_existing_permission_configuration_for_vue(permission))
        
    return JsonResponse({ "item_id": item_id, "item_model": request_data.get("item_model"), 
        "permissions" : permissions, "permission_configurations" : permission_configurations,
        "permission_pks": permission_pks })


@login_required
def add_permission_to_item(request):

    request_data = json.loads(request.body.decode('utf-8'))

    item_id = request_data.get("item_id")
    model_class = get_model(request_data.get("item_model"))
    target = model_class.objects.get(pk=item_id)

    permission_type = request_data.get("permission_type", None)
    permission_actors = request_data.get("permission_actors", None)
    permission_roles = request_data.get("permission_roles", None)
    permission_configuration = request_data.get("permission_configuration", None)

    permission_actors = [selection['pk'] for selection in permission_actors]
    permission_roles = [selection['name'] for selection in permission_roles]
    reformatted_permission_data = reformat_permission_data(permission_configuration)

    permissionClient = PermissionResourceClient(actor=request.user, target=target)

    action, result = permissionClient.add_permission(permission_type=permission_type, 
        permission_actors=permission_actors, permission_roles=permission_roles, 
        permission_configuration=reformatted_permission_data)

    action_dict = get_action_dict(action)
    permission_info = get_permission_info(result) if action.resolution.status == "implemented" else None
    action_dict.update({ "permission": permission_info, "item_id": item_id, "item_model": request_data.get("item_model") })

    return JsonResponse(action_dict)


@login_required
def delete_permission_from_item(request):

    request_data = json.loads(request.body.decode('utf-8'))

    permission_id = request_data.get("permission_id", None)

    item_id = request_data.get("item_id")
    model_class = get_model(request_data.get("item_model"))
    target = model_class.objects.get(pk=item_id)
    permissionClient = PermissionResourceClient(actor=request.user, target=target)
    permission_target = permissionClient.get_permission(pk=permission_id)
    conditionalClient = PermissionConditionalClient(actor=request.user, target=permission_target)

    # try to remove condition
    condition = conditionalClient.get_condition_template()
    if condition:
        action, result = conditionalClient.remove_condition(condition=condition)
        if action.resolution.status != "implemented":
            message = """In order to delete a permission, any conditions set on the permission must first be 
                deleted. The following condition on this permission could not be deleted: %s 
                It could not be deleted because: %s""" % (condition.get_name(), action.resolution.log)
            return JsonResponse({ "action_status": "failure", "action_log" : message })

    # now remove permission
    action, result = permissionClient.remove_permission(item_pk=permission_id)
    action_dict = get_action_dict(action)
    action_dict.update({ "removed_permission_pk": permission_id, "item_id": item_id, "item_model": request_data.get("item_model") })
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

    commentClient = CommentClient(actor=request.user, target=target)
    existing_comments = commentClient.get_all_comments_on_target()

    comment_pks, comments = [], {}
    for comment in existing_comments:
        comment_pks.append(comment.pk)
        comments.update(serialize_existing_comment_for_vue(comment))
        
    return JsonResponse({ "item_id": item_id, "item_model": request_data.get("item_model"), 
        "comments": comments, "comment_pks": comment_pks })


@login_required
def add_comment(request):

    request_data = json.loads(request.body.decode('utf-8'))

    item_id = request_data.get("item_id")
    model_class = get_model(request_data.get("item_model"))
    target = model_class.objects.get(pk=item_id)
    text = request_data.get("text")

    commentClient = CommentClient(actor=request.user, target=target)
    action, result = commentClient.add_comment(text=text)

    action_dict = get_action_dict(action)
    action_dict.update({ 'comment': serialize_existing_comment_for_vue(result) })
    return JsonResponse(action_dict)


@login_required
def edit_comment(request):

    request_data = json.loads(request.body.decode('utf-8'))

    item_id = request_data.get("item_id")
    model_class = get_model(request_data.get("item_model"))
    target = model_class.objects.get(pk=item_id)
    text = request_data.get("text")
    comment_pk = request_data.get("comment_pk")

    commentClient = CommentClient(actor=request.user, target=target)
    action, result = commentClient.edit_comment(pk=comment_pk, text=text)

    action_dict = get_action_dict(action)
    action_dict.update({ 'comment': serialize_existing_comment_for_vue(result) })
    return JsonResponse(action_dict)


@login_required
def delete_comment(request):

    request_data = json.loads(request.body.decode('utf-8'))

    item_id = request_data.get("item_id")
    model_class = get_model(request_data.get("item_model"))
    target = model_class.objects.get(pk=item_id)
    comment_pk = request_data.get("comment_pk")

    commentClient = CommentClient(actor=request.user, target=target)
    action, result = commentClient.delete_comment(pk=comment_pk)

    action_dict = get_action_dict(action)
    action_dict.update({ 'deleted_comment_pk': comment_pk })
    return JsonResponse(action_dict)