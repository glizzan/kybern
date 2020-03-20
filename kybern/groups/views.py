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


class GroupListView(generic.ListView):
    model = Group
    template_name = 'groups/group_list.html'


class GroupDetailView(generic.DetailView):
    model = Group
    template_name = 'groups/group_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Actions
        actionClient = ActionClient(actor=self.request.user, 
            target=self.object)
        context['actions'] = actionClient.get_action_history_given_target()
        # Role/Member info
        communityClient = CommunityClient(actor=self.request.user, target=self.object)
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


def add_role(request, target):

    request_data = json.loads(request.body.decode('utf-8'))

    communityClient = CommunityClient(actor=request.user)
    target = communityClient.get_community(community_pk=target)
    communityClient.set_target(target=target)
    
    action, result = communityClient.add_role(role_name=request_data['role_name'])
    
    return JsonResponse({
        "action_status": "success" if action.resolution.status == "implemented" else "error",
        "action_log": action.resolution.log
    })


def add_members(request, target):

    request_data = json.loads(request.body.decode('utf-8'))

    communityClient = CommunityClient(actor=request.user)
    target = communityClient.get_community(community_pk=target)
    communityClient.set_target(target=target)

    action, result = communityClient.add_members(member_pk_list=request_data["people_pks"])

    return JsonResponse({ "action_status": "success" if action.resolution.status == "implemented" else "error",
                        "action_log": action.resolution.log })


def remove_member(request, target):

    request_data = json.loads(request.body.decode('utf-8'))

    communityClient = CommunityClient(actor=request.user)
    target = communityClient.get_community(community_pk=target)
    communityClient.set_target(target=target)

    action, result = communityClient.remove_member(request_data['person_to_remove'])

    return JsonResponse({ "action_status": "success" if action.resolution.status == "implemented" else "error",
                          "action_log": action.resolution.log })


def add_people_to_role(request, target):

    request_data = json.loads(request.body.decode('utf-8'))

    communityClient = CommunityClient(actor=request.user)
    target = communityClient.get_community(community_pk=target)
    communityClient.set_target(target=target)

    action, result = communityClient.add_people_to_role(role_name=request_data['role_name'], 
        people_to_add=request_data['people_pks'])

    return JsonResponse({ "action_status": "success" if action.resolution.status == "implemented" else "error",
                          "action_log": action.resolution.log })


def remove_person_from_role(request, target):

    request_data = json.loads(request.body.decode('utf-8'))

    communityClient = CommunityClient(actor=request.user)
    target = communityClient.get_community(community_pk=target)
    communityClient.set_target(target=target)

    action, result = communityClient.remove_people_from_role(role_name=request_data['role_name'], 
        people_to_remove=request_data['person_to_remove'])

    return JsonResponse({ "action_status": "success" if action.resolution.status == "implemented" else "error",
                          "action_log": action.resolution.log })


def update_membership(request, target):

    request_data = json.loads(request.body.decode('utf-8'))

    communityClient = CommunityClient(actor=request.user)
    target = communityClient.get_community(community_pk=target)
    communityClient.set_target(target=target)

    actions = communityClient.update_role_membership(
        role_data={ 'rolename': request_data['role_name'], 'members': request_data['members']})

    action_errors = []
    for action in actions:
        if action.resolution.status != "implemented":
            action_errors.append(action.resolution.log)
    
    if action_erors:
        return JsonResponse({ "action_status": "error", "action_log": ", ".join(action_errors)})
    return JsonResponse({ "action_status": "success" })



###########################
### Stuff for edit role ###
###########################


def ready_condition_fields_for_display(condition):

    # NOTE: object type for non-existing data is Condition (as in ApprovalCondition) class not instance
    existing_data = True if condition.__class__.__name__ == "ConditionTemplate" else False
    condition_fields = condition.get_condition_type_class().get_configurable_fields() if existing_data else condition.get_configurable_fields()

    field_dict = []
    for field_name, field in condition_fields.items():
        # field.field syntax is because field object is actually DeferredAttribute wrapper
        required_text = "required" if field.field.blank else ""
        if existing_data:
            value = json.loads(condition.condition_data)[field_name]
        else:
            value = field.field.default
        field_dict.append({ 'name': field_name, 'type': field.field.__class__.__name__, 
            'required': required_text,  'value': value })

    return field_dict


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
    communityClient = CommunityClient(actor=request.user)
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
            { 'name' : obj.get_condition_type_class().descriptive_name, 'id': obj.pk,
            'configuration': ready_condition_fields_for_display(obj) } })

    # Get condition options
    settable_conditions = conditionalClient.get_possible_conditions()
    condition_options = [ { 'value': cond.__name__, 'text': cond.descriptive_name } for cond in settable_conditions ]

    # Create condition configuration 
    condition_configuration = { }
    for condition in settable_conditions:
        condition_configuration.update({ condition.__name__ : 
            { 'condition_name' : condition.descriptive_name, 
            'configuration': ready_condition_fields_for_display(condition) }  })
     
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

    communityClient = CommunityClient(actor=request.user)
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

    return JsonResponse({ "action_status": "success" if action.resolution.status == "implemented" else "error",
                          "action_log": action.resolution.log,
                          "permission_info": permission_info })


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

    return JsonResponse({ "action_status": action_status, "action_log": action_log,
        "new_display_name" : permission.full_description() })


def delete_permission(request, target):

    request_data = json.loads(request.body.decode('utf-8'))
    permission_id = request_data.get("permission_id", None)

    communityClient = CommunityClient(actor=request.user)
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

    return JsonResponse({ "action_status": "success" if action.resolution.status == "implemented" else "error",
                          "action_log": action.resolution.log })

                          
def reformat_condition_data(condition_data):
    if type(condition_data) == str:
        condition_data = json.loads(condition_data)
    reformatted_condition_data = {}
    for item in condition_data:
        if item['type'] == "BooleanField":
            item['value'] = True if item['value'] == "true" else item['value']
            item['value'] = False if item['value'] == "false" else item['value']
        if item['type'] in ["FloatField", "IntegerField"]: # Should probably treat floatfield differently
            item['value'] = int(item['value'])  # FIXME: implement try/catch and return as error?
        reformatted_condition_data.update({ item['name'] : item['value'] })
    print(json.dumps(reformatted_condition_data))
    return json.dumps(reformatted_condition_data)


def add_condition(request, target):

    request_data = json.loads(request.body.decode('utf-8'))
    condition_type = request_data.get("condition_type", None)
    condition_data = request_data.get("condition_data", None)
    permission_data = request_data.get("permission_data", None)   
    target_permission_id = request_data.get("target_permission_id", None)

    reformatted_condition_data = reformat_condition_data(condition_data)

    target_permission = PermissionResourceClient(actor=request.user).get_permission(pk=target_permission_id)
    conditionalClient = PermissionConditionalClient(actor=request.user, target=target_permission)

    action, result = conditionalClient.add_condition(condition_type=condition_type.lower(),
        condition_data=reformatted_condition_data, permission_data=permission_data)

    if action.resolution.status == "implemented":
        condition_info = {"name": result.get_condition_type_class().descriptive_name, 
            "configuration": ready_condition_fields_for_display(result), "id": result.pk }
    else:
        condition_info = None 

    return JsonResponse({ "action_status": "success" if action.resolution.status == "implemented" else "error",
                          "action_log": action.resolution.log,
                          "condition_info": condition_info })


def update_condition(request, target):

    request_data = json.loads(request.body.decode('utf-8'))
    permission_id = request_data.get("permission_id", None)
    condition_id = request_data.get("condition_id", None)
    configuration_data = request_data.get("condition_configuration", None)

    reformatted_condition_data = reformat_condition_data(configuration_data)

    #FIXME: the client call below doesn't require target
    permissionClient = PermissionResourceClient(actor=request.user)
    target_permission = permissionClient.get_permission(pk=permission_id)

    conditionClient = PermissionConditionalClient(actor=request.user, target=target_permission)
    action, result = conditionClient.change_condition(condition_pk=condition_id, permission_data=None, 
        condition_data=reformatted_condition_data)
    # FIXME: need to actually handle permission data

    return JsonResponse({ "action_status": action.resolution.status, "action_log": action.resolution.log,
        "new_display_name" : result.get_condition_type_class().descriptive_name })


def delete_condition(request, target):

    request_data = json.loads(request.body.decode('utf-8'))
    permission_id = request_data.get("permission_id", None)

    communityClient = CommunityClient(actor=request.user)
    target = communityClient.get_community(community_pk=target)
    permissionClient = PermissionResourceClient(actor=request.user, target=target)
    permission_target = permissionClient.get_permission(pk=permission_id)
    conditionalClient = PermissionConditionalClient(actor=request.user, target=permission_target)

    condition = conditionalClient.get_condition_template()
    action, result = conditionalClient.remove_condition(condition=condition)

    return JsonResponse({ "action_status": "success" if action.resolution.status == "implemented" else "error",
                          "action_log": action.resolution.log })
