"""
Decorators to help with data formatting, will almost definitely be moved into Concord.
"""

import json
from functools import wraps, partial


# Helper methods for reformatting


def reformat_role_select(permission_roles):
    """
    Test for expected input format:
        permission_roles = [{"name": "friends"}, {"name": "romans"}, {"name": "countrymen"}]

    If data is in that format, return in format:
        permission_roles = ["friends", "romans", "countrymen"]
    """
    if permission_roles and type(permission_roles[0]) == dict and "name" in permission_roles[0]:
        return [selection['name'] for selection in permission_roles]
    return permission_roles


def reformat_actor_select(permission_actors):
    """
    Test for expected input format:
        permission_actors = [{"pk": 1}]

    If data is in that format, return in format:
        permission_actors = [1, 2, 3]
    """
    if permission_actors and type(permission_actors[0]) == dict and "pk" in permission_actors[0]:
        return [int(selection['pk']) for selection in permission_actors]
    return permission_actors


def reformat_role_or_actor_field(field):
    """
    Expects some version of RoleField or ActorField, but doesn't break if it gets a
    different field type.
    """
    if field["type"] in ["RoleField", "RoleListField"]:

        # Single select treated differently
        if "other_data" in field and "multiple" in field["other_data"] and not field["other_data"]["multiple"]:
            field["value"] = field["value"]["name"] if field["value"] else field["value"]
        else:
            field["value"] = reformat_role_select(field["value"])

    if field["type"] in ["ActorField", "ActorListField"]:

        try:
            field["value"] = reformat_actor_select(field["value"])
        except IndexError:
            # if the above doesn't work, try to get by pk
            field["value"] = [int(data["value"]) for data in field["value"]] if field["value"] else []

    return field


def reformat_boolean_field(field):
    if field["type"] == "BooleanField":
        if field["value"] in ["true", "True"]:
            field["value"] = True
        if field["value"] in ["false", "False"]:
            field["value"] = False
    return field


def reformat_form_field_data(form_field_data):
    """
    Return format:

    [{'field_name': 'role_name', 'display': 'Roles people can be added to', 'type': 'RoleField',
    'required': False, 'value': [{'name': 'romans'}]}]
    """
    fields = {}
    for field in form_field_data:
        field = reformat_role_or_actor_field(field)
        field = reformat_boolean_field(field)
        fields.update({
            field["field_name"]: field["value"]
        })
    return fields


def reformat_supplied_fields(supplied_fields):

    reformatted_dict = {}
    for field in supplied_fields:
        if field["type"] in ["RoleField", "ActorField", "RoleListField", "ActorListField", "BooleanField", "IntegerField", "CharField"]:
            reformatted_dict[field["field_name"]] = reformat_role_or_actor_field(field)["value"]

    return reformatted_dict


def reformat_combined_permission_and_condition_data(combined_data):
    """
    Test for expected input format:

        [{'display': X, 'field_name': Y, 'type': Z, 'required': A, 'value': B}]

    Reformatting this data is a multi-step process.  We need to separate conditional and permission data,
    and reformat them separately.  We end up with something like:

        condition_data = { field_name: field_value, field_name: field_value }
        permission_data = [{permission_type: x, permission_actors: y, permission_roles: z }]

    """

    # Separate
    condition_fields = []
    permission_fields = []
    for field in combined_data:
        if "for_permission" in field and field["for_permission"]:
            permission_fields.append(field)
        else:
            condition_fields.append(field)

    # Reformat condition fields
    condition_fields = reformat_form_field_data(condition_fields)

    # Reformat permission-on-condition fields (handled differently than standalone permission data
    permission_field_data = {}
    for field in permission_fields:
        field = reformat_role_or_actor_field(field)  # keeps structure the same, just reformats value field
        if field["full_name"] not in permission_field_data:
            permission_field_data[field["full_name"]] = {"permission_type": field["full_name"]}
        if field["type"] in ["RoleField", "RoleListField"]:
            permission_field_data[field["full_name"]]["permission_roles"] = field["value"]
        if field["type"] in ["ActorField", "ActorListField"]:
            permission_field_data[field["full_name"]]["permission_actors"] = field["value"]

    permission_fields = []
    for field_name, field in permission_field_data.items():
        if field["permission_roles"] or field["permission_actors"]:
            permission_fields.append(field)

    return condition_fields, permission_fields


# Decorator


def reformat_input_data(function=None, expect_target=True):
    """Vuex sends data to Django views as JSON.  Here we unpack that JSON data into variables that can
    be passed directly to the Concord clients.  This also lets us do some re-formatting when, for
    example, our form data has the wrong structure."""

    if not callable(function):  # handles the case where we invoke decorator without calling it (aka no arguments)
        return partial(reformat_input_data, expect_target=expect_target)

    @wraps(function)
    def wrap(request, target=None, *args, **kwargs):

        if expect_target and target is None:
            raise ValueError("Function must be given a target, or pass expect_target=False to " +
                             "reformat_input_data decorator")

        request_data = json.loads(request.body.decode('utf-8'))  # loaded, we can now use this as our kwargs

        if "permission_roles" in request_data:
            request_data["permission_roles"] = reformat_role_select(request_data["permission_roles"])

        if "permission_actors" in request_data:
            request_data["permission_actors"] = reformat_actor_select(request_data["permission_actors"])

        if "combined_condition_data" in request_data:
            request_data["condition_data"], request_data["permission_data"] = \
                reformat_combined_permission_and_condition_data(request_data["combined_condition_data"])
            del(request_data["combined_condition_data"])

        if "supplied_fields" in request_data:
            request_data["supplied_fields"] = reformat_supplied_fields(request_data["supplied_fields"])

        # While we're here, we inspect function & kwargs and check required arguments.
        from inspect import signature
        for parameter_name, parameter_object in signature(function).parameters.items():
            if parameter_name in ["request", "target"]:
                continue
            if str(parameter_object.default) == "<class 'inspect._empty'>":   # if no default value for param
                if parameter_name not in request_data:
                    raise ValueError(f"Must supply parameter {parameter_name}")
                if request_data[parameter_name] in [None, "", [], {}]:
                    raise ValueError(f"Must give required parameter {parameter_name} a real value, " +
                                     f"not {request_data[parameter_name]}")

        return function(request, target, **request_data)

    return wrap
