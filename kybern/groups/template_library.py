"""Define templates targeting models in this app."""

from concord.actions.template_library import TemplateLibraryObject
from concord.utils.helpers  import Changes


class EmpowerPostersForumTemplate(TemplateLibraryObject):
    """Gives post authors near-total power over their posts, and any comments on their posts. Lets anyone comment."""
    name = "Posters Control Posts"
    scopes = ["forum"]
    description = """This template allows posters in a forum near-total control over their posts, as they can edit or delete
                     them without condition. They can also add, edit and delete comments on their posts. Any member can add,
                     edit, or delete their own comments, but they must get the original poster's approval."""

    def get_action_list(self):

        client = self.get_client()

        # Step 1: add permissions for authors to edit or delete their own posts, and add/edit/delete comments

        action_1 = client.PermissionResource.add_permission(
            permission_type=Changes().Groups.EditPost, anyone=True, permission_configuration={"author_only": True})
        action_1.target = "{{context.action.target}}"

        action_2 = client.PermissionResource.add_permission(
            permission_type=Changes().Groups.DeletePost, anyone=True, permission_configuration={"author_only": True})
        action_2.target = "{{context.action.target}}"

        action_3 = client.PermissionResource.add_permission(
            permission_type=Changes().Resources.EditComment, anyone=True,
            permission_configuration={"original_creator_only": True})
        action_3.target = "{{context.action.target}}"

        action_4 = client.PermissionResource.add_permission(
            permission_type=Changes().Resources.DeleteComment, anyone=True,
            permission_configuration={"original_creator_only": True})
        action_4.target = "{{context.action.target}}"

        action_5 = client.PermissionResource.add_permission(
            permission_type=Changes().Resources.AddComment, anyone=True,
            permission_configuration={"original_creator_only": True})
        action_5.target = "{{context.action.target}}"

        # Step 2: give other people ability to add comments if approved by original poster

        action_6 = client.PermissionResource.add_permission(permission_type=Changes().Resources.AddComment, anyone=True)
        action_6.target = "{{context.action.target}}"

        permission_data = [
            {"permission_type": Changes().Conditionals.Approve,
             "permission_actors": "{{nested:context.post.author||to_pk_in_list}}"},
            {"permission_type": Changes().Conditionals.Reject,
             "permission_actors": "{{nested:context.post.author||to_pk_in_list}}"}
        ]
        action_7 = client.Conditional.add_condition(
            condition_type="approvalcondition", permission_data=permission_data)
        action_7.target = "{{previous.5.result}}"

        # Step 3: give other people the ability to edit or delete their own comments IF they are the original commenter
        # AND they are approved by original poster

        action_8 = client.PermissionResource.add_permission(
            permission_type=Changes().Resources.EditComment, anyone=True,
            permission_configuration={"commenter_only": True})
        action_8.target = "{{context.action.target}}"

        action_9 = client.Conditional.add_condition(
            condition_type="approvalcondition", permission_data=permission_data)  # re-use permission data from before
        action_9.target = "{{previous.7.result}}"

        action_10 = client.PermissionResource.add_permission(
            permission_type=Changes().Resources.DeleteComment, anyone=True,
            permission_configuration={"commenter_only": True})
        action_10.target = "{{context.action.target}}"

        action_11 = client.Conditional.add_condition(
            condition_type="approvalcondition", permission_data=permission_data)  # re-use permission data from before
        action_11.target = "{{previous.9.result}}"

        return [action_1, action_2, action_3, action_4, action_5, action_6, action_7, action_8, action_9, action_10, action_11]


class ForumModeratorTemplate(TemplateLibraryObject):
    """Adds a 'moderator' role and gives them the ability to delete posts and comments."""
    name = "Forum Moderators"
    scopes = ["forum"]
    supplied_fields = {
        "initial_moderators":
            ["ActorListField", {"label": "Who should the initial moderators be?", "required": False}]
    }
    description = """This template creates a 'moderator' role and gives them the abilty do delete posts and comments within
                     a forum."""

    def get_action_list(self):

        client = self.get_client()

        # Step 1: create moderator role
        action_1 = client.Community.add_role(role_name="moderators")
        action_1.target = "{{context.group}}"

        # Step 2: add initial people to role
        action_2 = client.Community.add_people_to_role(
            role_name="moderators", people_to_add="{{supplied_fields.initial_moderators}}")
        action_2.target = "{{context.group}}"

        # Step 3: give moderators permission to delete posts
        action_3 = client.PermissionResource.add_permission(
            permission_type=Changes().Groups.DeletePost, permission_roles=["moderators"])

        # Step 4: give moderators permission to delete comments
        action_4 = client.PermissionResource.add_permission(
            permission_type=Changes().Resources.DeleteComment, permission_roles=["moderators"])

        return [action_1, action_2, action_3, action_4]


class BasicMemberRoleTemplate(TemplateLibraryObject):
    """Gives a wide variety of permissions to members, including: (a) the ability to add comments and edit and delete
    their own comments, (b) the ability to create new lists and forums and apply templates to them, and (c) the ability
    to add posts to forums."""
    name = "Basic Member Permissions"
    description = """Gives a wide variety of permissions to members, including: (a) the ability to add comments and
                     edit and delete their own comments, (b) the ability to create new lists and forums and apply
                    templates to them, and (c) the ability to add posts to forums."""
    scopes = ["role"]
    default_action_target = "{{context.group}}"

    def get_action_list(self):

        client = self.get_client()

        # Step 1: template permissions
        action_1 = client.PermissionResource.add_permission(
            permission_type=Changes().Actions.ApplyTemplate, permission_roles=["members"],
            permission_configuration={"original_creator_only": True})

        # Step 2: comment permissions
        action_2 = client.PermissionResource.add_permission(
            permission_type=Changes().Resources.AddComment, permission_roles=["members"])
        action_3 = client.PermissionResource.add_permission(
            permission_type=Changes().Resources.EditComment, permission_roles=["members"],
            permission_configuration={"commenter_only": True})
        action_4 = client.PermissionResource.add_permission(
            permission_type=Changes().Resources.DeleteComment, permission_roles=["members"],
            permission_configuration={"commenter_only": True})

        # Step 3: list permissions
        action_5 = client.PermissionResource.add_permission(
            permission_type=Changes().Resources.AddList, permission_roles=["members"])

        # Step 4: forum & post permissions
        action_6 = client.PermissionResource.add_permission(
            permission_type=Changes().Groups.AddForum, permission_roles=["members"])
        action_7 = client.PermissionResource.add_permission(
            permission_type=Changes().Groups.AddPost, permission_roles=["members"])

        return [action_1, action_2, action_3, action_4, action_5, action_6, action_7]
