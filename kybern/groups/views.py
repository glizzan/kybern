from django.views import generic
from django.http import HttpResponseRedirect, JsonResponse
import json

from django.urls import reverse
from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType

from concord.actions.client import ActionClient, TemplateClient
from concord.permission_resources.client import PermissionResourceClient
from concord.conditionals.client import ConditionalClient
from concord.resources.client import CommentClient
from concord.resources.models import Comment
from concord.actions.state_changes import Changes
from concord.permission_resources.models import PermissionsItem

from accounts.models import User
from .models import Group, Forum, Post
from .client import ForumClient, GroupClient
from .decorators import reformat_input_data



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

    if action.resolution.status in ["accepted", "implemented"]:
        return action.resolution.log, action.resolution.log     # unlikely to be displayed/accessed
    if action.resolution.status == "waiting":
        return "This action cannot be completed until a condition is passed.", action.resolution.log
    return readable_log_dict.get(action.resolution.log, "We're sorry, there was an error"), action.resolution.log


def process_action(action):

    if action.resolution.status == "implemented":
        action_verb = ""
        follow_up = "They did so because they have the permission %s." % action.resolution.approved_through
    else:
        action_verb = "tried to "
        follow_up = ""  # TODO: what goes here?

    action_time = action.created_at.strftime("%b %d %Y %I:%M%p")
    if action.target:
        action_description = f"{action.change.description_past_tense()} {action.target.get_name()}"
    else:
        action_description = action.change.description_past_tense()

    action_string = f"At {action_time}, {action.actor.username} {action_verb}{action_description}. {follow_up}"

    # Check for condition  ( FIXME: we need a much more performant way of doing this )
    conditionalClient = ConditionalClient(actor="system")
    conditions = conditionalClient.get_condition_items_for_action(action_pk=action.pk)
    
    return {
        "action_pk": action.pk,
        "action_target_pk": action.object_id,
        "action_target_model": action.target.__class__.__name__,   # will this work???
        "action_target_content_type": action.content_type.pk,
        "description": action.get_description(),
        "created": str(action.created_at),
        "display_date": action_time,
        "actor": action.actor.username,
        "status": action.resolution.status,
        "resolution passed by": action.resolution.approved_through,
        "display": action_string,
        "is_template": action.change.get_change_type() == Changes.Actions.ApplyTemplate,
        "has_condition": {
            "exists": True if conditions else False,
            "conditions": [ { "pk": condition.pk, "type": condition.__class__.__name__ } for condition in conditions ]
        }
    }


# FIXME: why are get_action_dict and process_actions two different things?
def get_action_dict(action, fetch_template_actions=False):
    display_log, developer_log = make_action_errors_readable(action)
    return {
        "action_created": True if action.resolution.status in ["implemented", "approved", "waiting", "rejected"] else False,
        "action_status": action.resolution.status,
        "action_pk": action.pk,
        "action_log": display_log,
        "action_developer_log": developer_log,
        "is_template": action.change.get_change_type() == Changes.Actions.ApplyTemplate
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


def serialize_existing_permission_for_vue(permission, pk_as_key=True):
    """  (note: this matches format specified in vuex store)
    permissions: {{ permissions }},         
        // { int(pk) : { name: x, display: x, change_type: x } } """

    permission_dict = { "name": permission.full_description(), "display": permission.display_string(), 
            "change_type": permission.change_type, "actors": permission.get_actors(), "roles": permission.get_role_names(),
            "anyone": permission.anyone, "fields": permission.get_configuration() }

    if permission.has_condition():
        condition_data = permission.get_condition_data(info="basic")
        condition_data["fields"] = permission.get_condition_data(info="fields")
    else:
        condition_data = None
    permission_dict.update({ "condition": condition_data })

    if pk_as_key:
        return { permission.pk : permission_dict }
    return permission_dict


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
    template_name = 'groups/groups/group_list.html'


class GroupCreateView(LoginRequiredMixin, generic.edit.CreateView):
    model = Group
    template_name = 'groups/groups/group_create.html'
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
    template_name = 'groups/groups/group_detail.html'

    def prep_clients(self):
        self.communityClient = GroupClient(actor=self.request.user, target=self.object)
        self.permissionClient = PermissionResourceClient(actor=self.request.user, target=self.object)
        self.actionClient = ActionClient(actor=self.request.user, target=self.object)
        self.conditionalClient = ConditionalClient(actor=self.request.user)
        self.forumClient = ForumClient(actor=self.request.user, target=self.object)

    def add_user_data_to_context(self, context):

        # Governance info
        context['owners'] = self.communityClient.target.roles.get_owners()
        context['governors'] = self.communityClient.target.roles.get_governors()
        context['governance_info'] = json.dumps(self.communityClient.get_governance_info_as_text())
        context['owner_condition'] = json.dumps(self.communityClient.get_condition_data(leadership_type="owner"))
        context['governor_condition'] = json.dumps(self.communityClient.get_condition_data(leadership_type="governor"))

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
            // { model_name: [ { value: x , text: x } ], model_name: [ { value: x , text: x }  ] }
        permission_configuration_options: {{ permission_configuration_options }},
            // { fieldname: { display: x, type: x, required: x, value: x, field_name: x } }
        """

        context["permission_options"] = {}
        context["permission_configuration_options"] = {}

        for model_class in [Group, Forum, Post, Comment, PermissionsItem]:

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
        return context        


####################
### Forums Views ###
####################


@login_required
def change_group_name(request):

    request_data = json.loads(request.body.decode('utf-8'))
    group_pk = request_data.get("group_pk")
    new_name = request_data.get("new_name")

    communityClient = GroupClient(actor=request.user)
    target = communityClient.get_community(community_pk=group_pk)
    communityClient.set_target(target=target)

    action, result = communityClient.change_name(new_name=new_name)
    action_dict = get_action_dict(action)
    action_dict["group_name"] = new_name
    return JsonResponse(action_dict)


@login_required
def change_group_description(request):

    request_data = json.loads(request.body.decode('utf-8'))
    group_pk = request_data.get("group_pk")
    new_description = request_data.get("new_description")

    communityClient = GroupClient(actor=request.user)
    target = communityClient.get_community(community_pk=group_pk)
    communityClient.set_target(target=target)

    action, result = communityClient.change_group_description(new_description=new_description)
    action_dict = get_action_dict(action)
    action_dict["group_description"] = new_description
    return JsonResponse(action_dict)


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
    if action.resolution.status == "implemented":
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
    if action.resolution.status == "implemented":
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

    permission_pks, permissions = [], {}
    for permission in existing_permissions:
        permission_pks.append(permission.pk)
        permissions.update(serialize_existing_permission_for_vue(permission))
        
    return permission_pks, permissions


@login_required
def get_data_for_role(request, target):

    actor = request.user
    communityClient = GroupClient(actor=actor)
    target = communityClient.get_community(community_pk=target)
    request_data = json.loads(request.body.decode('utf-8'))
    role_name = request_data['role_name']
    
    permission_pks, permissions = get_permissions_given_role(actor, target, role_name)

    return JsonResponse({ "permissions" : permissions, "role_permissions": permission_pks })


def get_permission_info(permission):
    return {
        "pk": permission.pk,
        "permission_data": list(serialize_existing_permission_for_vue(permission).values())
    }


def get_permission_target_helper(request, target, item_or_role, item_id, item_model):

    if item_or_role == "item":                  # If an item has been passed in, make it the target
        model_class = get_model(item_model)
        return model_class.objects.get(pk=item_id)
    if item_or_role == "role":    # Otherwise the role the community is set on is the target
        communityClient = GroupClient(actor=request.user)
        return communityClient.get_community(community_pk=target)
        

@login_required
@reformat_input_data
def add_permission(request, target, permission_type, item_or_role, permission_actors=None, 
        permission_roles=None, permission_configuration=None, item_id=None, item_model=None):

    target = get_permission_target_helper(request, target, item_or_role, item_id, item_model)
    permissionClient = PermissionResourceClient(actor=request.user, target=target)

    action, result = permissionClient.add_permission(permission_type=permission_type, 
        permission_actors=permission_actors, permission_roles=permission_roles, 
        permission_configuration=permission_configuration)

    action_dict = get_action_dict(action)
    permission_info = get_permission_info(result) if action.resolution.status == "implemented" else None
    action_dict.update({ "permission": permission_info, "item_id": item_id, "item_model": item_model })
    return JsonResponse(action_dict)


@login_required
@reformat_input_data
def update_permission(request, target, permission_id, item_or_role, permission_actors=None,
        permission_roles=None, permission_configuration=None, item_id=None, item_model=None):

    target = get_permission_target_helper(request, target, item_or_role, item_id, item_model)
    permissionClient = PermissionResourceClient(actor=request.user, target=target)
    target_permission = permissionClient.get_permission(pk=permission_id)

    actions = permissionClient.update_configuration(configuration_dict=permission_configuration, 
        permission=target_permission)

    if permission_actors:
        actor_actions = permissionClient.update_actors_on_permission(actor_data=permission_actors, 
            permission=target_permission)
        actions += actor_actions
    if permission_roles:
        role_actions = permissionClient.update_roles_on_permission(role_data=permission_roles, 
            permission=target_permission)
        actions += role_actions

    action_dict = get_multiple_action_dicts(actions)

    permission = permissionClient.get_permission(pk=permission_id)  # get refreshed version
    permission_info = get_permission_info(permission)
    action_dict.update({ "permission" : permission_info })

    return JsonResponse(action_dict)


@login_required
@reformat_input_data
def delete_permission(request, target, permission_id, item_or_role, item_id=None, item_model=None):

    target = get_permission_target_helper(request, target, item_or_role, item_id, item_model)
    permissionClient = PermissionResourceClient(actor=request.user, target=target)

    # now remove permission
    action, result = permissionClient.remove_permission(item_pk=permission_id)
    action_dict = get_action_dict(action)
    action_dict.update({ "removed_permission_pk": permission_id })
    return JsonResponse(action_dict)


####################################
### Views for setting conditions ###
####################################

# NOTE that there are no "update condition" functions, for now we simply use add as update and overwrite the whole thing


@login_required
@reformat_input_data
def add_condition(request, target, condition_type, permission_or_leadership, target_permission_id=None,
    leadership_type=None, condition_data=None, permission_data=None):

    communityClient = GroupClient(actor=request.user)
    target = communityClient.get_community(community_pk=target)

    if permission_or_leadership == "permission":

        permClient = PermissionResourceClient(actor=request.user, target=target)
        action, result = permClient.add_condition_to_permission(permission_pk=target_permission_id,
            condition_type=condition_type, condition_data=condition_data, permission_data=permission_data)
        if action.resolution.status == "implemented": 
            condition_data = result.get_condition_data(info="all")
        
    elif permission_or_leadership == "leadership":

        communityClient.set_target(target=target)
        action, result = communityClient.add_leadership_condition(condition_type=condition_type, 
            leadership_type=leadership_type, condition_data=condition_data, permission_data=permission_data)
        if action.resolution.status == "implemented":
            condition_data = target.get_condition_data(leadership_type=leadership_type, info="all")

    action_dict = get_action_dict(action)
    action_dict.update({ "condition_info": condition_data, "permission_or_leadership": permission_or_leadership,
        "leadership_type": leadership_type, "target_permission_id": target_permission_id })
    return JsonResponse(action_dict)


@login_required
@reformat_input_data
def remove_condition(request, target, permission_or_leadership, target_permission_id=None, leadership_type=None):

    communityClient = GroupClient(actor=request.user)
    target = communityClient.get_community(community_pk=target)

    if permission_or_leadership == "permission":

        permClient = PermissionResourceClient(actor=request.user, target=target)
        action, result = permClient.remove_condition_from_permission(permission_pk=target_permission_id)
    
    elif permission_or_leadership == "leadership":

        communityClient.set_target(target=target)
        action, result = communityClient.remove_leadership_condition(leadership_type=leadership_type)    

    action_dict = get_action_dict(action)
    action_dict.update({ "permission_or_leadership": permission_or_leadership,
        "leadership_type": leadership_type, "target_permission_id": target_permission_id })
    return JsonResponse(action_dict)


#############################################
### Views for interacting with conditions ###
#############################################


@login_required
def update_approval_condition(request):

    request_data = json.loads(request.body.decode('utf-8'))
    condition_pk = request_data.get("condition_pk", None)
    action_to_take = request_data.get("action_to_take", None)

    conditionalClient = ConditionalClient(actor=request.user)
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

    conditionalClient = ConditionalClient(actor=request.user)
    voteClient = conditionalClient.get_vote_condition_as_client(pk=condition_pk)
    
    action, result = voteClient.vote(vote=action_to_take)

    return JsonResponse(get_action_dict(action))


@login_required
def get_conditional_data(request):

    request_data = json.loads(request.body.decode('utf-8'))
    condition_pk = request_data.get("condition_pk", None)
    condition_type = request_data.get("condition_type", None)

    conditionalClient = ConditionalClient(actor=request.user)
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
### Misc permission views ###
#############################


@login_required
def get_permissions(request):

    request_data = json.loads(request.body.decode('utf-8'))

    item_id = request_data.get("item_id")
    model_class = get_model(request_data.get("item_model"))
    target = model_class.objects.get(pk=item_id)

    permClient = PermissionResourceClient(actor=request.user, target=target)

    existing_permissions = permClient.get_all_permissions()

    permission_pks, permissions = [], {}
    for permission in existing_permissions:
        permission_pks.append(permission.pk)
        permissions.update(serialize_existing_permission_for_vue(permission))

    return JsonResponse({ "item_id": item_id, "item_model": request_data.get("item_model"), "permissions": permissions,
        "permission_pks": permission_pks, "foundational": target.foundational_permission_enabled, 
        "governing": target.governing_permission_enabled })


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
    permissionClient = PermissionResourceClient(actor=request.user, target=target)

    enable_or_disable = request_data.get("enable_or_disable")
    governing_or_foundational = request_data.get("governing_or_foundational")
    
    if governing_or_foundational == "governing":
        if enable_or_disable == "enable":
            action, result = permissionClient.enable_governing_permission()
        elif enable_or_disable == "disable":
            action, result = permissionClient.disable_governing_permission()
    elif governing_or_foundational == "foundational":
        if enable_or_disable == "enable":
            action, result = permissionClient.enable_foundational_permission()
        elif enable_or_disable == "disable":
            action, result = permissionClient.disable_foundational_permission()

    action_dict = get_action_dict(action)
    action_dict.update({ "item_id": item_id, "item_model": request_data.get("item_model"),
        "foundational": result.foundational_permission_enabled, "governing": result.governing_permission_enabled
    })    
    return JsonResponse(action_dict)


@login_required
def toggle_anyone(request):

    request_data = json.loads(request.body.decode('utf-8'))
    permission_id = request_data.get("permission_id")
    enable_or_disable = request_data.get("enable_or_disable")

    permissionClient = PermissionResourceClient(actor=request.user)
    target_permission = permissionClient.get_permission(pk=permission_id)

    if enable_or_disable == "enable":
        action, result = permissionClient.give_anyone_permission(permission_pk=target_permission.pk)
    elif enable_or_disable == "disable":
        action, result = permissionClient.remove_anyone_from_permission(permission_pk=target_permission.pk)

    action_dict = get_action_dict(action)
    action_dict.update({ "permission": get_permission_info(result) })

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


######################
### Template Views ###
######################


def serialize_template_for_vue(template, pk_as_key=True):
    template_dict = {
        "pk": template.pk,
        "name": template.name,
        "description": template.user_description,
        "supplied_fields": template.get_supplied_form_fields()
    }
    if pk_as_key:
        return { template.pk: template_dict }
    return template_dict 


@login_required
@reformat_input_data(expect_target=False)   # target passed in is empty
def get_templates_for_scope(request, target, scope):
    templateClient = TemplateClient(actor=request.user)
    templates = templateClient.get_templates_for_scope(scope=scope)
    template_dict = [serialize_template_for_vue(template, pk_as_key=False) for template in templates]
    response_dict = { 'templates': template_dict, 'scope': scope }
    return JsonResponse(response_dict)


@login_required
@reformat_input_data
def apply_template(request, target, template_model_pk, supplied_fields=None):

    target_object = GroupClient(actor=request.user).get_community(community_pk=target)
    templateClient = TemplateClient(actor=request.user, target=target_object)
    action, result = templateClient.apply_template(template_model_pk=template_model_pk, 
        supplied_fields=supplied_fields)

    action_dict = get_action_dict(action)
    return JsonResponse(action_dict)


@login_required
@reformat_input_data(expect_target=False)
def get_applied_template_data(request, target, trigger_action_pk):

    actionClient = ActionClient(actor=request.user)
    container = actionClient.get_container_given_trigger_action(action_pk=trigger_action_pk)
    container_data = actionClient.get_container_data(container_pk=container.pk)

    container_info = { "container_status": container.get_overall_status() }

    action_data = []
    for item in container_data:

        condition_data = []
        for condition in item["conditions"]:
            ct = ContentType.objects.get_for_id(condition["ct"])
            condition_data.append({ "pk": condition["pk"], "ct": condition["ct"], "type": ct.model_class().__name__})

        action_data.append({
            "action_pk": item["action"].pk if item["action"] else None,
            "action_actor": item["action"].actor.pk if item["action"] else None,
            "action_change_description": item["action"].change.description if item["action"] else None,
            "result_pk": item["result"].pk if item["result"] else None,
            "result_model": item["result"].__class__.__name__ if item["result"] else None,
            "conditions": condition_data
        })

    container_info["action_data"] = action_data

    return JsonResponse({ "trigger_action_pk": trigger_action_pk, "container_info": container_info })
    



########################
### Membership Views ###
########################


@login_required
def check_membership_permissions(request, target):
    """
    Checks for "join group", "leave group", "add members" and "remove members" permissions.  In the templates
    there's a button that says "waiting memberships" that goes to things that have open conditions, if the
    user clicks through THEN we look for permission related to that, using a different function.
    """

    group_client = GroupClient(actor=request.user)
    group_client.set_target(target=group_client.get_community(community_pk=target))
    perm_client = PermissionResourceClient(actor=request.user)

    group_members = group_client.target.roles.get_users_given_role("members")

    # join group - checks if user in group and, if not, check if has permission to join group
    join_group = False if request.user.pk in group_members else \
        perm_client.has_permission(group_client, "add_members", {"member_pk_list" : [request.user.pk]})
            
    # "leave group" - checks if user in group and, if true, check if use rhas permission to leave group
    leave_group = False if request.user.pk not in group_members else \
        perm_client.has_permission(group_client, "remove_members", {"member_pk_list" : [request.user.pk]})

    # gets a separate user to test add_members and remove_members.  note that perm_client's has_permission does
    # not check validation here, so it doesn't matter who the user is.
    test_user = User.objects.first() if User.objects.first().pk != request.user.pk else User.objects.last()
    add_members = perm_client.has_permission(group_client, "add_members", {"member_pk_list" : [test_user.pk]})
    remove_members = perm_client.has_permission(group_client, "remove_members", {"member_pk_list" : [test_user.pk]})

    return JsonResponse({"user_permissions" : {"join_group": join_group, "leave_group": leave_group, "add_members": add_members,
        "remove_members": remove_members}})


