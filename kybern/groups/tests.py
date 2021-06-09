import json

from django.test import TestCase
from django.urls import reverse


class UrlTestCase(TestCase):
    maxDiff = None

    def test_url_views_without_target(self):
        response = self.client.get(reverse('generate_url_map'))
        self.assertEquals(
            response.json()['urls'],
            {
                "apply_template":"groups/api/apply_template/",
                "get_templates_for_scope":"groups/api/get_templates_for_scope/",
                "get_comment_data":"groups/api/get_comment_data/",
                "update_consensus_condition":"groups/api/update_consensus_condition/",
                "update_vote_condition":"groups/api/update_vote_condition/",
                "get_conditional_data":"groups/api/get_conditional_data/",
                "get_action_data_for_target":"groups/api/get_action_data_for_target/",
                "get_action_data":"groups/api/get_action_data/",
                "change_item_permission_override":"groups/api/change_item_permission_override/",
                "get_permissions":"groups/api/get_permissions/",
                "get_permission":"groups/api/get_permission/",
                "generate_url_map":"groups/api/get_urls/",
                "create_group":"groups/create-group/",
                "group_create":"groups/create/",
                "group_list":"groups/list/"
            }
        )

    def test_url_views_with_target(self):
        expected_dict = {
            "get_documents":"groups/api/1/get_documents/",
            "get_list":"groups/api/1/get_list/",
            "get_lists":"groups/api/1/get_lists/",
            "apply_template":"groups/api/apply_template/",
            "get_templates_for_scope":"groups/api/get_templates_for_scope/",
            "get_comment_data":"groups/api/get_comment_data/",
            "get_post":"groups/api/1/get_post/",
            "get_posts_for_forum":"groups/api/1/get_posts/",
            "get_forum":"groups/api/1/get_forum/",
            "get_forums":"groups/api/1/forums/",
            "update_consensus_condition":"groups/api/update_consensus_condition/",
            "update_vote_condition":"groups/api/update_vote_condition/",
            "get_conditional_data":"groups/api/get_conditional_data/",
            "get_action_data_for_target":"groups/api/get_action_data_for_target/",
            "get_action_data":"groups/api/get_action_data/",
            "remove_condition":"groups/api/remove_condition/1/",
            "edit_condition":"groups/api/edit_condition/1/",
            "add_condition":"groups/api/add_condition/1/",
            "check_permissions":"groups/api/check_permissions/1/",
            "check_permission":"groups/api/check_permission/1/",
            "toggle_anyone":"groups/api/toggle_anyone/1/",
            "change_item_permission_override":"groups/api/change_item_permission_override/",
            "get_permissions":"groups/api/get_permissions/",
            "get_permission":"groups/api/get_permission/",
            "delete_permission":"groups/api/delete_permission/1/",
            "update_permission":"groups/api/update_permission/1/",
            "add_permission":"groups/api/add_permission/1/",
            "get_data_for_role":"groups/api/get_data_for_role/1/",
            "take_proposed_action":"groups/api/1/take_proposed_action",
            "take_action":"groups/api/1/take_action",
            "get_forum_data":"groups/api/get_forum_data/1/",
            "get_permission_data":"groups/api/get_permission_data/1/",
            "get_governance_data":"groups/api/get_governance_data/1/",
            "generate_url_map_with_target":"groups/api/get_urls/1/",
            "generate_url_map":"groups/api/get_urls/",
            "create_group":"groups/create-group/",
            "export_as_json":"groups/export/json/1",
            "export_as_csv":"groups/export/csv/1",
            "group_create":"groups/create/",
            "group_list":"groups/list/"
        }
        response = self.client.get(reverse('generate_url_map_with_target', kwargs={"target": 1}))
        self.assertEquals(response.json()['urls'], expected_dict)
        self.assertEquals(len(response.json()['urls']), len(expected_dict))
