from django.views import generic
from django.http import HttpResponseRedirect, JsonResponse
import json

from django.urls import reverse

from django.contrib.auth.models import User
from concord.actions.client import ActionClient
from concord.communities.client import CommunityClient
from concord.permission_resources.client import PermissionResourceClient
from concord.conditionals.client import PermissionConditionalClient

from .models import Group


# FIXME: this probably doesn't belong here
class GroupClient(CommunityClient):
    """Easy way to replace the default community model with the one we want to use here, group."""
    community_model = Group


class GroupListView(generic.ListView):
    model = Group
    template_name = 'groups/group_list.html'


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


def process_actions(action_queryset):
    """Helper method, gets action data and saves it as list of dicts for Vue to use."""

    actions = []
    
    for action in action_queryset:
        actions.append(process_action(action))

    return json.dumps(actions)


class GroupDetailView(generic.DetailView):
    model = Group
    template_name = 'groups/group_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Actions
        actions = ActionClient(actor=self.request.user, 
            target=self.object).get_action_history_given_target()
        context['actions'] = process_actions(actions)
        context['recent_actions'] = process_actions(actions.order_by('updated_at')[:5])
        # Role/Member info
        communityClient = GroupClient(actor=self.request.user, target=self.object)
        context['username_map'] = { person.pk : person.username for person in User.objects.all() }
        context['current_members'] = [member.pk for member in communityClient.get_members()]
        context['potential_members'] = list(set(context['username_map'].keys()).difference(set(context['current_members'])))

        # Role Info
        context['roles'] = [ { 'role_name': role_name, 'current_members': role_data } 
                                        for role_name, role_data in communityClient.get_custom_roles().items() ]
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


#####################################################
### Helper methods, likely to be moved to concord ###
#####################################################


def get_action_dict(action):
    return { 
        "action_created": True if action.resolution.status in ["implemented", "approved", "waiting", "rejected"] else False,
        "action_status": action.resolution.status,
        "action_log": action.resolution.log, 
        "action_pk": action.pk,
    }


def add_role(request, target):

    request_data = json.loads(request.body.decode('utf-8'))

    communityClient = GroupClient(actor=request.user)
    target = communityClient.get_community(community_pk=target)
    communityClient.set_target(target=target)
    
    action, result = communityClient.add_role(role_name=request_data['role_name'])
    
    return JsonResponse(get_action_dict(action))


def add_members(request, target):

    request_data = json.loads(request.body.decode('utf-8'))

    communityClient = GroupClient(actor=request.user)
    target = communityClient.get_community(community_pk=target)
    communityClient.set_target(target=target)

    action, result = communityClient.add_members(member_pk_list=request_data["people_pks"])

    return JsonResponse(get_action_dict(action))


def remove_member(request, target):

    request_data = json.loads(request.body.decode('utf-8'))

    communityClient = GroupClient(actor=request.user)
    target = communityClient.get_community(community_pk=target)
    communityClient.set_target(target=target)

    action, result = communityClient.remove_members(request_data['person_to_remove'])

    return JsonResponse(get_action_dict(action))


def add_people_to_role(request, target):

    request_data = json.loads(request.body.decode('utf-8'))

    communityClient = GroupClient(actor=request.user)
    target = communityClient.get_community(community_pk=target)
    communityClient.set_target(target=target)

    action, result = communityClient.add_people_to_role(role_name=request_data['role_name'], 
        people_to_add=request_data['people_pks'])

    return JsonResponse(get_action_dict(action))


def remove_person_from_role(request, target):

    request_data = json.loads(request.body.decode('utf-8'))

    communityClient = GroupClient(actor=request.user)
    target = communityClient.get_community(community_pk=target)
    communityClient.set_target(target=target)

    action, result = communityClient.remove_people_from_role(role_name=request_data['role_name'], 
        people_to_remove=request_data['person_to_remove'])

    return JsonResponse(get_action_dict(action))


###########################
### Stuff for edit role ###
###########################


def ready_permission_fields_for_display(permission):

    # NOTE: object type for none-existing data is State Change Object class not instance
    existing_data = True if permission.__class__.__name__ == "PermissionsItem" else False
    permission_fields = permission.get_configuration() if existing_data else permission.get_configurable_fields()

    fields = []
    if existing_data:
        for key, value in permission_fields.items():
            fields.append({'name': key, 'value': value})
    else:
        for field in permission_fields:
            fields.append({'name': field, 'value': None})

    return fields


def get_permissions_given_role(request, target):

    request_data = json.loads(request.body.decode('utf-8'))

    permissionClient = PermissionResourceClient(actor=request.user)
    communityClient = GroupClient(actor=request.user)
    target = communityClient.get_community(community_pk=target)
    permissionClient.set_target(target=target)

    ### Prep permissions

    # Get existing permissions
    existing_permissions = permissionClient.get_permissions_associated_with_role(role_name=request_data['role_name'])
    
    # Serialize them for vue
    serialized_existing_permissions = []
    for permission in existing_permissions:
        serialized_existing_permissions.append({ "id": permission.pk, 
            "name": permission.full_description(), "display": permission.full_description(), 
            "change_type": permission.change_type,
            "configuration": ready_permission_fields_for_display(permission) })

    # Get permission options
    settable_permissions = permissionClient.get_settable_permissions(return_format="state_change_objects")
    permission_options = [ { "value": perm.get_change_type(), "text": perm.description } for perm in settable_permissions ]

    # Create permission configuration options
    permission_configuration = {}
    for sco in settable_permissions:
        permission_configuration[sco.get_change_type()] = ready_permission_fields_for_display(sco)                      
           
    ### Prep conditions
    
    # Get existing conditions
    conditionalClient = PermissionConditionalClient(actor=request.user)
    existing_conditions = conditionalClient.get_conditions_given_targets(
            target_pks=[permission.pk for permission in existing_permissions])
    
    # Serialize them for vue
    serialized_existing_conditions = {}    
    for obj in existing_conditions:
        serialized_existing_conditions.update({ obj.conditioned_object_id : 
            { 'name' : obj.condition_name(), 'id': obj.pk, 'display': obj.condition_description(),
            'configuration': obj.condition_data.get_configurable_fields_with_data() } })

    # Get condition options
    settable_conditions = conditionalClient.get_possible_conditions()
    condition_options = [ { 'value': cond.__name__, 'text': cond.descriptive_name } for cond in settable_conditions ]

    # Create condition configuration 
    condition_configuration = { }
    for condition in settable_conditions:
        condition_configuration.update({ condition.__name__ : 
            { 'condition_name' : condition.descriptive_name, 
            'configuration': condition.get_configurable_fields() }  })
     
    return JsonResponse({ 
        "existing_permissions": serialized_existing_permissions,
        "permission_options": permission_options,
        "permission_configuration": permission_configuration,
        "existing_conditions": serialized_existing_conditions,
        "condition_options": condition_options,
        "condition_configuration": condition_configuration
    })


def reformat_permission_data(permission_data):
    result = { field['name'] : field['value'] for field in permission_data }
    return result


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

    if action.resolution.status == "implemented":
        permission_info = {"id": result.pk, "name": result.get_name(), 
            "display": result.full_description(), "change_type": result.change_type, 
            "configuration": ready_permission_fields_for_display(result) }
    else:
        permission_info = None

    action_dict = get_action_dict(action)
    action_dict.update({ "permission_info": permission_info })
    return JsonResponse(action_dict)


def update_permission(request, target):

    request_data = json.loads(request.body.decode('utf-8'))
    permission_id = request_data.get("permission_id", None)
    permission_configuration = request_data.get("permission_configuration", None)

    reformatted_permission_data = reformat_permission_data(permission_configuration)

    permissionClient = PermissionResourceClient(actor=request.user)
    target_permission = permissionClient.get_permission(pk=permission_id)
    permissionClient.set_target(target=target_permission)
    actions = permissionClient.update_configuration(configuration_dict=reformatted_permission_data, 
        permission=target_permission)

    action_log = ""
    action_status = "success"
    for action in actions:
        if action.resolution.status != "implemented":
            action_status = "error"
            action_log += action.resolution.log

    permission = permissionClient.get_permission(pk=permission_id)  # get refreshed version

    action_dict = get_action_dict(action)
    action_dict.update({ "new_display_name" : permission.full_description() })
    return JsonResponse(action_dict)


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
    return JsonResponse(get_action_dict(action))


def process_configuration_data(configuration_data):
    """Splits configuration data into condition_data and permission_data."""
    configuration_data = json.loads(configuration_data) if type(configuration_data) == str else configuration_data
    condition_data = []
    permission_data = []
    for field in configuration_data:
        if field["type"] in ["PermissionRoleField", "PermissionActorField"]:
            if field["value"]:
                field["value"] = [item.strip() for item in field["value"].split(",")] 
            else:
                field["value"] = []
            permission_data.append(field)
        else:
            condition_data.append(field)
    return condition_data, permission_data

                          
def add_condition(request, target):

    request_data = json.loads(request.body.decode('utf-8'))
    target_permission_id = request_data.get("target_permission_id", None)
    condition_type = request_data.get("condition_type", None)
    configuration_data = request_data.get("condition_configuration", None)

    condition_data, permission_data = process_configuration_data(configuration_data)

    target_permission = PermissionResourceClient(actor=request.user).get_permission(pk=target_permission_id)
    conditionalClient = PermissionConditionalClient(actor=request.user, target=target_permission)

    action, result = conditionalClient.add_condition(condition_type=condition_type.lower(),
        condition_data=condition_data, permission_data=permission_data)

    if action.resolution.status == "implemented":
        condition_info = {"name": result.condition_name(), 
            "display": result.condition_description(),
            "configuration": result.condition_data.get_configurable_fields_with_data(), "id": result.pk }
    else:
        condition_info = None 

    action_dict = get_action_dict(action)
    action_dict.update({ "condition_info": condition_info })
    return JsonResponse(action_dict)


def update_condition(request, target):

    request_data = json.loads(request.body.decode('utf-8'))
    permission_id = request_data.get("permission_id", None)
    condition_id = request_data.get("condition_id", None)
    configuration_data = request_data.get("condition_configuration", None)

    condition_data, permission_data = process_configuration_data(configuration_data)

    #FIXME: the client call below doesn't require target
    permissionClient = PermissionResourceClient(actor=request.user)
    target_permission = permissionClient.get_permission(pk=permission_id)

    conditionClient = PermissionConditionalClient(actor=request.user, target=target_permission)
    action, result = conditionClient.change_condition(condition_pk=condition_id,
        condition_data=condition_data, permission_data=permission_data)

    action_dict = get_action_dict(action)
    action_dict.update({ "new_display_name" : result.condition_name() })
    return JsonResponse(action_dict)


def delete_condition(request, target):

    request_data = json.loads(request.body.decode('utf-8'))
    permission_id = request_data.get("permission_id", None)

    communityClient = GroupClient(actor=request.user)
    target = communityClient.get_community(community_pk=target)
    permissionClient = PermissionResourceClient(actor=request.user, target=target)
    permission_target = permissionClient.get_permission(pk=permission_id)
    conditionalClient = PermissionConditionalClient(actor=request.user, target=permission_target)

    condition = conditionalClient.get_condition_template()
    action, result = conditionalClient.remove_condition(condition=condition)

    return JsonResponse(get_action_dict(action))


#####################################
### CONDITION-SPECIFIC INTERFACES ###
#####################################

def update_approval_condition(request, target):

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
    

def get_condition_data(request, target):

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

    return JsonResponse({ "permission_details" : permission_details,
        "condition_details" : { 
            "status": condition.condition_status(),
            "display_status": condition.display_status(),
            "fields": condition.display_fields()
        }
    })


def get_action_data(request):

    request_data = json.loads(request.body.decode('utf-8'))
    action_pk = request_data.get("action_pk", None)

    action = ActionClient(actor=request.user).get_action_given_pk(action_pk)

    return JsonResponse({ "action_data": process_action(action) })