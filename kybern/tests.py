import time, os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from splinter import Browser
from django.conf import settings
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from unittest import skipIf

from django import db
from django.contrib.auth.models import User
from concord.utils.helpers import Changes, Client
from groups.models import Forum
from concord.actions.models import TemplateModel

settings.DEBUG = True
chrome_options = webdriver.ChromeOptions()

if os.environ.get("GITHUB_ACTIONS") or settings.RUN_HEADLESS:
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')

display_test_cases = True

test_cases_to_skip = [
    # "AccountsTestCase",
    # "ActionConditionsTestCase",
    # "ActionsTestCase",
    # "ApprovalConditionsTestCase",
    # "ConsensusConditionTestCase",
    # "DependentFieldTestCase",
    # "DocumentTestCase",
    # "ForumsTestCase",
    # "GroupBasicsTestCase",
    # "ListTestCase",
    # "MembershipTestCase",
    # "MultipleConditionsTestCase",
    # "PermissionsTestCase",
    # "TemplatesTestCase",
    # "VotingConditionTestCase",
]


class BaseTestCase(StaticLiveServerTestCase):
    """BaseTestCase contains all setup & teardown used universally by tests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = Browser('chrome', options=chrome_options)
        cls.browser.wait_time = 10
        if display_test_cases:
            print("running ", cls.__name__)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.browser.quit()

    @classmethod
    def create_users(cls):
        for user_name in ["meganrapinoe", "christenpress", "tobinheath", "crystaldunn", "julieertz",
                          "caseyshort", "emilysonnett", "midgepurce"]:
            User.objects.create_user(user_name, 'shaunagm@gmail.com', 'badlands2020')

    @classmethod
    def create_templates(cls):
        # Create templates (note that this servces as a test that all templates can be instantiated)
        from django.core.management import call_command
        call_command('update_templates', recreate=True, verbosity=0)

    def tearDown(self):
        time.sleep(3)  # FIXME: give time for db to be torn down, you can turn this off if you don't mind lots of passing tests with errors printing

    def login_user(self, username, password):
        self.browser.visit(self.live_server_url + "/login/")
        self.browser.fill('username', username)
        self.browser.fill('password', password)
        self.browser.find_by_id('submit_login').first.click()

    def get_selected_in_multiselect(self, search_within=None):
        base = search_within if search_within else self.browser
        names = []
        for item in base.find_by_css(".multiselect__tag"):
            names.append(item.text)
        return names

    def delete_selected_in_multiselect(self, username):
        for item in self.browser.find_by_css(".multiselect__tag"):
            if item.text == username:
                item.find_by_css(".multiselect__tag-icon").first.click()
                return True
        return False

    def select_from_multiselect(self, selection, element_css=".multiselect__element", search_within=None, index=0):
        """Helper method to select options given the custom interface vue-multiselect provides."""
        base = search_within if search_within else self.browser
        base.find_by_css(".multiselect__select")[index].click()
        time.sleep(.25)
        for item in base.find_by_css(element_css):
            if selection in item.text:
                item.click()
                return True
        return False

    def go_to_group(self, group_name):
        """Helper method to navigate to group detail page, used because liveservertestcase is finicky about
        pks."""
        self.browser.visit(self.live_server_url + "/groups/list/")
        self.browser.find_by_text(group_name).first.click()

    def go_to_edit_role(self, role_name):
        self.browser.find_by_id('governance_button', wait_time=5)[0].click()
        self.browser.find_by_id("customroles").first.click()
        time.sleep(4)
        role_id = role_name + "_editrole"
        self.browser.find_by_id(role_id, wait_time=5).first.click()
        time.sleep(4)

    def add_condition_to_permission(self, condition_type, role_choice=None, actor_choice=None):
        """Note that this assumes we're going to configure the condition by only adding a role to the first
        role field."""
        self.browser.find_by_css('.add-condition').first.click()
        self.browser.select("condition_select", condition_type)
        if role_choice:
            dropdown = self.browser.find_by_css(".permissionrolefield", wait_time=5)[0]
            self.select_from_multiselect(role_choice, search_within=dropdown)
        if actor_choice:
            dropdown = self.browser.find_by_css(".permissionactorfield", wait_time=5)[0]
            self.select_from_multiselect(actor_choice, search_within=dropdown)
        self.browser.find_by_css('.condition-ok').first.click()
        self.take_action()
        time.sleep(3)

    def click_through_link_in_response_and_open_condition(self):
        self.browser.find_by_id('condition_link', wait_time=5)[0].click()
        self.browser.find_by_css('.action-condition', wait_time=5)[0].click()

    def go_to_most_recent_action_in_history_and_open_condition(self):
        self.browser.find_by_id('group_history_button')[0].click()
        self.browser.find_by_css(".action-link-button")[0].click()
        self.browser.find_by_css('.action-condition', wait_time=5)[0].click()

    def add_role(self, role_name):
        self.browser.find_by_id('governance_button', wait_time=5)[0].click()
        self.browser.find_by_id("customroles").first.click()
        self.browser.find_by_id('add_role_button', wait_time=5).first.click()
        self.browser.fill('role_name', role_name)
        time.sleep(3)  # pause while check_permissions enables
        self.take_action()

    def approve_action(self, approved=True):
        self.assertTrue(self.browser.is_text_present('Please approve or reject this action.'))
        time.sleep(4)
        index = 0 if approved else 1
        self.take_action(index)
        time.sleep(2)
        verb = "approved" if approved else "rejected"
        text = f"You have successfully {verb}. If you want to provide context for this action, you can do so here."
        self.assertTrue(self.browser.is_text_present(text))

    def go_to_membership_settings(self):
        self.browser.find_by_id('governance_button', wait_time=5).first.click()
        self.browser.find_by_id("membership", wait_time=5).first.click()
        self.browser.find_by_id('group_membership_settings_button', wait_time=5).first.click()

    def add_membership_permission(self, first_role_selection):
        self.go_to_membership_settings()
        time.sleep(5)
        self.browser.find_by_css('.add-permission', wait_time=5).first.click()
        time.sleep(3)
        self.browser.find_by_id("add_audience", wait_time=5).first.click()
        self.select_from_multiselect(first_role_selection, index=2)
        self.take_action()
        time.sleep(1)

    def add_member(self, member_name, remove=False):
        self.browser.find_by_id('governance_button', wait_time=5)[0].click()
        self.browser.find_by_id("membership", wait_time=5).first.click()
        time.sleep(2)
        if remove:
            self.browser.find_by_id('remove_members_display_button', wait_time=5).first.click()
        else:
            self.browser.find_by_id('add_members_display_button', wait_time=5).first.click()
        time.sleep(2)
        self.select_from_multiselect(selection=member_name)
        self.take_action()

    def check_if_take_action_disabled(self, should_be_disabled=True, index=0, added_wait=0, alt_format=False):
        time.sleep(added_wait)
        time.sleep(20)
        if alt_format:
            element = self.browser.find_by_css(".action-mode-options label")[0]
        else:
            element = self.browser.find_by_css('.take-action', wait_time=5)[index]
        if should_be_disabled:
            self.assertTrue(element.has_class('disabled'))
        else:
            self.assertFalse(element.has_class('disabled'))

    def fill_out_add_or_edit_form(self, pairs, close=True):  # pairs is dict
        time.sleep(3)  # seems to be important for loading purposes
        for key, value in pairs.items():
            self.browser.fill(key, value)
        time.sleep(1)
        self.take_action()
        time.sleep(3)
        if close:
            self.close_modal()

    def click_edit_perm_by_display_name(self, display_name):
        elements = self.browser.find_by_css(".edit-perm")
        for el in elements:
            parent = el.find_by_xpath('..')
            if display_name.strip(" ") == parent.text.strip(" "):
                el.click()
                return
        print("Could not find element matching ", display_name)

    def click_edit_cond_by_display_name(self, display_name, index=None):
        elements = self.browser.find_by_css(".existing-condition")
        for count, el in enumerate(elements):
            if display_name.strip(" ") == el.text.strip(" "):
                if not index or index == count:
                    el.click()
                    return
        print("Could not find element matching ", display_name)

    def take_action(self, index=0):
        if index == "last":
            self.browser.find_by_css('.take-action', wait_time=5).last.click()
        self.browser.find_by_css('.take-action', wait_time=5)[index].click()

    def close_modal(self, index=0):
        if index == "last":
            self.browser.find_by_css(".close", wait_time=5).last.click()
        self.browser.find_by_css(".close", wait_time=5)[index].click()

    def take_action_and_close(self, response=None, index=0):
        self.take_action(index)
        if response:
            self.assertTrue(self.browser.is_text_present(response, wait_time=5))
        else:
            time.sleep(3)
        self.close_modal()
        if len(self.browser.find_by_css(".close")) > 0:
            self.close_modal()

    def apply_template(self, template_name, supplied_role_field=None):
        id_str = "select_template_" + template_name
        self.browser.find_by_id(id_str, wait_time=5).first.click()
        if supplied_role_field:
            dropdown = self.browser.find_by_css(".permissionrolefield")[0]
            self.select_from_multiselect(supplied_role_field, search_within=dropdown)
        self.browser.find_by_id('submit_apply_template', wait_time=5).first.click()
        time.sleep(3)

    def apply_membership_template(self, template_name, supplied_role_field=None):
        self.browser.find_by_id("membership", wait_time=5).first.click()
        self.browser.find_by_id('group_membership_settings_button', wait_time=5).first.click()
        self.browser.find_by_id('membership_templates_link', wait_time=5).first.click()
        time.sleep(6)
        self.apply_template(template_name, supplied_role_field)

    def get_permissions(self, text=False):
        if text:
            return [item.text for item in self.browser.find_by_css(".permissions-row", wait_time=5)]
        return self.browser.find_by_css(".permissions-row", wait_time=5)

    def check_member_count(self, count_str):
        self.browser.find_by_id('governance_button', wait_time=5).first.click()
        self.browser.find_by_id("customroles", wait_time=5).first.click()
        self.browser.find_by_id('members_member_count', wait_time=5)[0].scroll_to()
        time.sleep(2)
        self.assertEquals(self.browser.find_by_id('members_member_count', wait_time=5)[0].text, count_str)

    def check_permission_table_cell(self, row, column, has_perm, has_info):
        css_string = ".perm-cell." + column + "." + row
        elem = self.browser.find_by_css(css_string)
        if has_perm:
            self.assertTrue(elem.has_class('has-perm'))
        else:
            self.assertFalse(elem.has_class('has-perm'))
        if has_info:
            self.assertTrue(elem.has_class('has-info'))
        else:
            self.assertFalse(elem.has_class('has-info'))


@skipIf("AccountsTestCase" in test_cases_to_skip, "")
class AccountsTestCase(BaseTestCase):

    def setUp(self):
        self.create_users()

    def test_register_account(self):
        """Tests that we can register a new user account."""
        self.browser.visit(self.live_server_url)
        self.browser.links.find_by_text('Sign In')[0].scroll_to()
        self.browser.links.find_by_text('Sign In').first.click()
        self.browser.links.find_by_text('Register an account').first.click()
        self.browser.fill('username', 'cheynamatthews')
        self.browser.fill('email', 'example@example.com')
        self.browser.fill('access_code', 'alpha-fhhe')
        self.browser.fill('password1', 'elephant!?')
        self.browser.fill('password2', 'elephant!?')
        self.browser.find_by_id('submit_registration').first.click()
        self.assertTrue(self.browser.is_text_present('Thank you for registering!'))

    def test_login(self):
        """Tests that we can log in an existing user."""
        self.browser.visit(self.live_server_url)
        self.browser.links.find_by_text('Sign In')[0].scroll_to()
        self.browser.links.find_by_text('Sign In').first.click()
        self.browser.fill('username', 'meganrapinoe')
        self.browser.fill('password', 'badlands2020')
        self.browser.find_by_id('submit_login').first.click()
        self.assertTrue(self.browser.is_text_present('Profile: meganrapinoe'))


@skipIf("ActionConditionsTestCase" in test_cases_to_skip, "")
class ActionConditionsTestCase(BaseTestCase):

    def setUp(self):

        # Basic setup
        self.create_users()
        self.create_templates()
        self.actor = User.objects.first()
        self.client = Client(actor=self.actor)
        self.community = self.client.Community.create_community(name="USWNT")
        self.client.update_target_on_all(target=self.community)
        self.client.Community.add_members_to_community(member_pk_list=[user.pk for user in User.objects.all()])
        self.client.Community.add_role_to_community(role_name="forwards")
        pinoe = User.objects.get(username="meganrapinoe")
        press = User.objects.get(username="christenpress")
        heath = User.objects.get(username="tobinheath")
        self.client.Community.add_people_to_role(role_name="forwards", people_to_add=[pinoe.pk, press.pk, heath.pk])

        # Permission setup
        action, self.permission = self.client.PermissionResource.add_permission(
            change_type=Changes().Communities.AddRole, roles=["forwards"])

    def test_adding_condition_to_permission_generates_condition(self):

        # Pinoe adds condition to permission
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.go_to_edit_role("forwards")
        self.browser.find_by_css('.edit-perm').first.click()   # clicks edit on the first permission
        self.add_condition_to_permission("VoteCondition", role_choice="forwards")

        # Someone with the permission tries to take action (use asserts to check for condition error text)
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.add_role('midfielders')
        self.assertTrue(self.browser.is_text_present(
            'There is a condition on your action which must be resolved before your action can be implemented.', wait_time=5))

        # Click through to condition
        self.click_through_link_in_response_and_open_condition()
        self.assertTrue(self.browser.is_text_present('Please cast your vote', wait_time=5))


@skipIf("ActionsTestCase" in test_cases_to_skip, "")
class ActionsTestCase(BaseTestCase):

    def setUp(self):
        self.create_users()
        self.create_templates()
        self.actor = User.objects.first()
        self.client = Client(actor=self.actor)
        self.community = self.client.Community.create_community(name="USWNT")
        self.client.update_target_on_all(target=self.community)
        self.client.Community.add_members_to_community(member_pk_list=[user.pk for user in User.objects.all()])

    def test_taking_action_generates_action(self):

        # Add role
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.add_role('forwards')
        self.close_modal()

        # Check for action in action history
        self.browser.find_by_id('group_history_button')[0].click()
        time.sleep(5)
        self.assertTrue(self.browser.is_text_present('meganrapinoe added role forwards'))


@skipIf("ApprovalConditionsTestCase" in test_cases_to_skip, "")
class ApprovalConditionsTestCase(BaseTestCase):

    def setUp(self):

        # create group, add members, add roles, add members to role
        self.create_users()
        self.create_templates()
        self.actor = User.objects.first()
        self.client = Client(actor=self.actor)
        self.community = self.client.Community.create_community(name="USWNT")
        self.client.update_target_on_all(target=self.community)
        self.client.Community.add_members_to_community(member_pk_list=[user.pk for user in User.objects.all()])
        self.client.Community.add_role_to_community(role_name="forwards")
        pinoe = User.objects.get(username="meganrapinoe")
        press = User.objects.get(username="christenpress")
        heath = User.objects.get(username="tobinheath")
        self.client.Community.add_people_to_role(role_name="forwards", people_to_add=[pinoe.pk, press.pk, heath.pk])

        # add permission & condition to permission
        action, self.permission = self.client.PermissionResource.add_permission(
            change_type=Changes().Communities.AddRole, roles=["forwards"])
        perm_data = [
            {"permission_type": Changes().Conditionals.Approve, "permission_roles": ["forwards"]},
            {"permission_type": Changes().Conditionals.Reject, "permission_roles": ["forwards"]}
        ]
        self.client.Conditional.set_target(self.permission)
        self.client.Conditional.add_condition(condition_type="approvalcondition", permission_data=perm_data)

        # have person take action that triggers permission/condition
        self.client.Community.set_actor(heath)
        self.client.Community.add_role_to_community(role_name="midfielders")

    def test_approve_implements_action(self):

        # User navigates to action history and approves action
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.go_to_most_recent_action_in_history_and_open_condition()
        self.approve_action()

        # Check action is implemented
        self.browser.reload()
        self.browser.find_by_id('group_history_button')[0].click()
        time.sleep(2)
        css_str = "#action_history_table_element > tbody > tr:nth-child(1)"
        self.assertTrue("implemented" in self.browser.find_by_css(css_str)[0].text)

    def test_reject_rejects_action(self):

        # User navigates to action history and rejects
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.go_to_most_recent_action_in_history_and_open_condition()
        self.approve_action(False)

        # Check action is rejected
        self.browser.reload()
        self.browser.find_by_id('group_history_button')[0].click()
        time.sleep(2)
        css_str = "#action_history_table_element > tbody > tr:nth-child(1)"
        self.assertTrue("rejected" in self.browser.find_by_css(css_str)[0].text)

    def test_person_without_permission_to_approve_cant_approve(self):
        self.login_user("emilysonnett", "badlands2020")
        self.go_to_group("USWNT")
        self.go_to_most_recent_action_in_history_and_open_condition()
        result = self.browser.find_by_css(".take-action.disabled")
        self.assertTrue(len(result) == 2)


@skipIf("ConsensusConditionTestCase" in test_cases_to_skip, "")
class ConsensusConditionTestCase(BaseTestCase):

    def setUp(self):
        self.create_users()
        self.create_templates()
        self.actor = User.objects.first()
        self.client = Client(actor=self.actor)
        self.community = self.client.Community.create_community(name="USWNT")
        self.client.update_target_on_all(target=self.community)
        self.client.Community.add_members_to_community(member_pk_list=[user.pk for user in User.objects.all()])
        self.client.Community.add_role_to_community(role_name="forwards")
        self.client.Community.add_role_to_community(role_name="defense")
        self.client.Community.add_role_to_community(role_name="captains")
        pinoe = User.objects.get(username="meganrapinoe")
        press = User.objects.get(username="christenpress")
        heath = User.objects.get(username="tobinheath")
        sonny = User.objects.get(username="emilysonnett")
        crystal = User.objects.get(username="crystaldunn")
        self.client.Community.add_people_to_role(
            role_name="forwards", people_to_add=[pinoe.pk, press.pk, heath.pk, crystal.pk])
        self.client.Community.add_people_to_role(
            role_name="defense", people_to_add=[sonny.pk, crystal.pk])
        self.client.Community.add_people_to_role(
            role_name="captains", people_to_add=[pinoe.pk, press.pk])

    def test_minimum_duration(self):

        # set up permission & condition
        action, self.permission = self.client.PermissionResource.add_permission(
            change_type=Changes().Communities.AddRole, roles=["defense"]
        )
        perm_data = [
            {"permission_type": Changes().Conditionals.RespondConsensus,
             "permission_roles": ["forwards"]},
            {"permission_type": Changes().Conditionals.ResolveConsensus,
             "permission_roles": ["captains"]}
        ]
        self.client.Conditional.set_target(self.permission)
        self.client.Conditional.add_condition(condition_type="consensuscondition", permission_data=perm_data)

        # player triggers condition, it cannot be resolved yet
        self.login_user("emilysonnett", "badlands2020")
        self.go_to_group("USWNT")
        self.add_role('midfielders')
        self.assertTrue(self.browser.is_text_present(
            "There is a condition on your action which must be resolved before your action can be implemented."))
        self.click_through_link_in_response_and_open_condition()
        self.assertTrue(self.browser.is_text_present(
            'The discussion cannot be resolved until the minimum duration of 2 days has passed.'))
        self.assertTrue(self.browser.is_text_present('You are not a participant in this consensus decision.'))

    def test_loose_consensus_condition(self):

        # set up permission & condition
        action, self.permission = self.client.PermissionResource.add_permission(
            change_type=Changes().Communities.AddRole, roles=["defense"]
        )
        perm_data = [
            {"permission_type": Changes().Conditionals.RespondConsensus,
             "permission_roles": ["forwards"]},
            {"permission_type": Changes().Conditionals.ResolveConsensus,
             "permission_roles": ["captains"]}
        ]
        self.client.Conditional.set_target(self.permission)
        self.client.Conditional.add_condition(
            condition_type="consensuscondition", permission_data=perm_data, condition_data={"minimum_duration": 0})

        # player triggers condition
        self.login_user("crystaldunn", "badlands2020")
        self.go_to_group("USWNT")
        self.add_role('midfielders')
        self.assertTrue(self.browser.is_text_present(
            "There is a condition on your action which must be resolved before your action can be implemented."))
        self.click_through_link_in_response_and_open_condition()
        self.assertTrue(self.browser.is_text_present(
            'The minimum duration of has passed. If the discussion was resolved right now, the result would be: rejected.'))

        # Crystal adds support, it is now passing
        self.assertEquals(self.browser.find_by_id('support_names').first.value, "")
        self.browser.find_by_id('user_response_radio_buttons')[0].scroll_to()
        self.browser.find_by_css("#user_response_radio_buttons > label:first-child").first.click()
        self.browser.find_by_id('submit_response').first.click()
        time.sleep(3)
        self.assertEquals(self.browser.find_by_id('support_names').first.value, "crystaldunn")
        self.assertTrue(self.browser.is_text_present(
            'The minimum duration of has passed. If the discussion was resolved right now, the result would be: approved.'))

        # another player adds block, is no longer passing
        self.login_user("tobinheath", "badlands2020")
        self.go_to_group("USWNT")
        self.go_to_most_recent_action_in_history_and_open_condition()
        self.browser.find_by_id('user_response_radio_buttons')[0].scroll_to()
        self.browser.find_by_css("#user_response_radio_buttons > label:nth-child(4)").first.click()
        self.browser.find_by_id('submit_response').first.click()
        time.sleep(3)
        self.assertEquals(self.browser.find_by_id('block_names').first.value, "tobinheath")
        self.assertTrue(self.browser.is_text_present(
            'The minimum duration of has passed. If the discussion was resolved right now, the result would be: rejected.'))

        # player removes block
        self.browser.find_by_css("#user_response_radio_buttons > label:nth-child(3)").first.click()
        self.browser.find_by_id('submit_response').first.click()
        self.assertTrue(self.browser.is_text_present(
            'The minimum duration of has passed. If the discussion was resolved right now, the result would be: approved.'))

        # player tries to resolve, can't because they're not a captain so they don't even get the link
        self.assertFalse(self.browser.is_text_present('Resolve this discussion?'))

        # captain resolves (christen)
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.go_to_most_recent_action_in_history_and_open_condition()
        self.browser.find_by_id('resolve_button').first.click()
        self.assertTrue(self.browser.is_text_present('The condition was resolved with resolution approved. Your response was no response.'))

        # change is implemented
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button').first.click()
        self.browser.find_by_id("customroles").first.click()
        time.sleep(2)
        roles = [item.text for item in self.browser.find_by_css(".role_name_display")]
        self.assertEquals(roles, ["members", "forwards", "defense", "captains", "midfielders"])

    def test_strict_consensus_condition(self):

        # set up permission & condition
        action, self.permission = self.client.PermissionResource.add_permission(
            change_type=Changes().Communities.AddRole, roles=["defense"]
        )
        perm_data = [
            {"permission_type": Changes().Conditionals.RespondConsensus,
             "permission_roles": ["forwards"]},
            {"permission_type": Changes().Conditionals.ResolveConsensus,
             "permission_roles": ["captains"]}
        ]
        self.client.Conditional.set_target(self.permission)
        self.client.Conditional.add_condition(condition_type="consensuscondition", permission_data=perm_data,
                                              condition_data={"minimum_duration": 0, "is_strict": True})

        # player triggers condition
        self.login_user("crystaldunn", "badlands2020")
        self.go_to_group("USWNT")
        self.add_role("midfielders")
        self.assertTrue(self.browser.is_text_present(
            "There is a condition on your action which must be resolved before your action can be implemented."))
        self.click_through_link_in_response_and_open_condition()
        self.assertTrue(self.browser.is_text_present(
            'The minimum duration of has passed. If the discussion was resolved right now, the result would be: rejected.'))

        # players respond, but it won't pass until all have responded so it keeps saying it would be rejected

        self.assertEquals(self.browser.find_by_id('support_names').first.value, "")
        self.browser.find_by_id('user_response_radio_buttons')[0].scroll_to()
        self.browser.find_by_css("#user_response_radio_buttons > label:first-child").first.click()
        self.browser.find_by_id('submit_response').first.click()
        time.sleep(3)
        self.assertEquals(self.browser.find_by_id('support_names').first.value, "crystaldunn")
        self.assertTrue(self.browser.is_text_present(
            'The minimum duration of has passed. If the discussion was resolved right now, the result would be: rejected.'))

        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.go_to_most_recent_action_in_history_and_open_condition()
        self.browser.find_by_id('user_response_radio_buttons')[0].scroll_to()
        self.browser.find_by_css("#user_response_radio_buttons > label:first-child").first.click()
        self.browser.find_by_id('submit_response').first.click()
        time.sleep(3)
        self.assertEquals(self.browser.find_by_id('support_names').first.value, "christenpress, crystaldunn")
        self.assertTrue(self.browser.is_text_present(
            'The minimum duration of has passed. If the discussion was resolved right now, the result would be: rejected.'))

        # resolves with not enough people responding so rejected
        self.browser.find_by_id('resolve_button').first.click()
        self.assertTrue(self.browser.is_text_present('The condition was resolved with resolution rejected. Your response was support.'))


@skipIf("DependentFieldTestCase" in test_cases_to_skip, "")
class DependentFieldTestCase(BaseTestCase):

    def setUp(self):

        # Basic setup
        self.create_users()
        self.create_templates()
        self.actor = User.objects.first()
        self.client = Client(actor=self.actor)
        self.community = self.client.Community.create_community(name="USWNT")
        self.client.update_target_on_all(target=self.community)
        self.client.Community.add_members_to_community(member_pk_list=[user.pk for user in User.objects.all()[:4]])
        self.client.Community.add_role_to_community(role_name="forwards")
        pinoe = User.objects.get(username="meganrapinoe")
        press = User.objects.get(username="christenpress")
        self.client.Community.add_people_to_role(role_name="forwards", people_to_add=[pinoe.pk, press.pk])

        # delete default membership permission
        from concord.permission_resources.models import PermissionsItem
        for permission in PermissionsItem.objects.all():
            if permission.change_type == Changes().Communities.AddMembers:
                permission.delete()

    def test_the_dependent_field_created_by_posters_control_posts_template_works(self):

        # Delete existing comment permission on Forum
        from concord.permission_resources.models import PermissionsItem
        for permission in PermissionsItem.objects.all():
            if permission.change_type == Changes().Resources.AddComment:
                permission.delete()

        # Creator applies "posters control posts" template to Governance Forum
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_css(".forum-link", wait_time=5).first.click()
        time.sleep(3)  # for some bizarre reason, without this sleep splinter confuses perm button for history button
        self.browser.find_by_id("forum_permissions", wait_time=5).first.click()
        self.browser.find_by_id("apply_templates", wait_time=5).first.click()
        time.sleep(2)
        self.browser.find_by_id("select_template_posters_control_posts", wait_time=5).first.click()
        self.browser.find_by_id("submit_apply_template", wait_time=5).first.click()
        time.sleep(4)
        self.browser.back()
        self.browser.find_by_css(".forum-link", wait_time=5).first.click()
        self.browser.find_by_id("forum_permissions", wait_time=5).first.click()
        time.sleep(3)
        permissions = [item.text for item in self.browser.find_by_css(".permissions-row")]
        self.assertEquals(len(permissions), 7)

        # Inspecting what was created, everything looks fine
        time.sleep(3)
        self.click_edit_perm_by_display_name("edit comment")
        time.sleep(4)
        self.click_edit_cond_by_display_name("Approval Condition")
        time.sleep(4)
        self.assertTrue(self.browser.is_text_present("set as: post's author"))
        self.browser.find_by_css(".edit-dependent-field", wait_time=5).first.click()
        self.assertTrue(self.browser.is_text_present("Choose object to depend on:"))
        self.assertEquals(self.browser.find_by_id("model_options").first.value, "actiongroupcommentpost")
        self.assertEquals(len(self.browser.find_by_id("depend_on_model_post")), 1)
        self.assertTrue(self.browser.find_by_id("depend_on_model_post").first.has_class('btn-info'))
        field_select = self.browser.find_by_css(".dependent-field-select").first
        time.sleep(1)
        self.assertEquals(field_select.value, "author")

        # User makes a post
        self.go_to_group("USWNT")
        self.browser.find_by_css(".forum-link", wait_time=5).first.click()
        self.browser.find_by_id('add_post_default_button', wait_time=5).first.click()
        self.fill_out_add_or_edit_form(pairs={"title": "I have an idea", "content": "It's a good one"})
        self.assertTrue(self.browser.is_text_present('I have an idea', wait_time=5))

        # Another user makes a comment on the post
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_css(".forum-link").first.click()
        self.browser.find_by_css(".post-link").first.click()
        self.browser.find_by_id('add_comment_default_button').first.click()
        self.fill_out_add_or_edit_form(pairs={"text": "it's ok I guess"})
        self.assertFalse(self.browser.is_text_present("it's ok I guess", wait_time=5))

        # User approves it
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_css(".forum-link", wait_time=5).first.click()
        self.browser.find_by_css(".post-link", wait_time=5).first.click()
        self.browser.find_by_id("post_history_button", wait_time=5).first.click()
        self.browser.find_by_css(".action-link-button", wait_time=5)[0].click()
        self.browser.find_by_css('.action-condition', wait_time=5)[0].click()
        self.approve_action()
        time.sleep(3)
        self.browser.back()
        self.browser.back()
        self.assertTrue(self.browser.is_text_present("it's ok I guess", wait_time=5))

    def test_make_dependent_field_from_scratch(self):

        # user adds a membership permission where members can add people
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.add_membership_permission("members")

        # adds an approval condition with permission_actors dependency field as member_pk_list
        time.sleep(2)
        self.browser.find_by_css('.add-condition', wait_time=5).first.click()
        self.browser.select("condition_select", "ApprovalCondition")
        time.sleep(2)
        self.browser.find_by_css('.add-dependent-field', wait_time=5)[1].click()
        time.sleep(6)
        self.browser.find_by_id('depend_on_model_action', wait_time=5).first.click()
        self.browser.select('dependent-field-select', 'member_pk_list')
        self.browser.find_by_id('save-dependent-field', wait_time=5).first.click()
        time.sleep(5)
        self.browser.find_by_css('.condition-ok', wait_time=5)[0].click()
        time.sleep(1)
        self.take_action()
        time.sleep(1)

        # user adds member which kicks off a condition, with approves set via dependency field as member_pk_list
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.add_member("midgepurce")
        text_to_match = 'There is a condition on your action which must be resolved before your action can be implemented.'
        self.assertTrue(self.browser.is_text_present(text_to_match, wait_time=5))

        # Christen doesn't have permission to approve the invite
        self.click_through_link_in_response_and_open_condition()
        self.check_if_take_action_disabled(should_be_disabled=True, index=0, added_wait=5)  # approve is first action

        # Midge approves, and now there are 5 members
        self.login_user("midgepurce", "badlands2020")
        self.go_to_group("USWNT")
        self.go_to_most_recent_action_in_history_and_open_condition()
        self.check_if_take_action_disabled(should_be_disabled=False, index=0, added_wait=5)
        self.approve_action()
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button', wait_time=5).first.click()
        self.browser.find_by_id("customroles", wait_time=5).first.click()
        self.browser.find_by_id('members_member_count', wait_time=5)[0].scroll_to()
        time.sleep(2)
        self.assertEquals(self.browser.find_by_id('members_member_count', wait_time=5).text, "5 people")



@skipIf("DocumentTestCase" in test_cases_to_skip, "")
class DocumentTestCase(BaseTestCase):

    def setUp(self):

        # Basic setup
        self.create_users()
        self.create_templates()
        self.actor = User.objects.first()
        self.client = Client(actor=self.actor)
        self.community = self.client.Community.create_community(name="USWNT")
        self.client.update_target_on_all(target=self.community)
        self.client.Community.add_members_to_community(member_pk_list=[user.pk for user in User.objects.all()[:4]])
        self.client.Community.add_role_to_community(role_name="forwards")
        pinoe = User.objects.get(username="meganrapinoe")
        press = User.objects.get(username="christenpress")
        self.client.Community.add_people_to_role(role_name="forwards", people_to_add=[pinoe.pk, press.pk])

    def test_basic_document_functionality(self):

        # create a document
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('add_document_default_button').first.click()
        self.fill_out_add_or_edit_form(
            pairs={"name": "Why we deserve equal pay", "description": "Obviously"}, close=True)
        self.assertTrue(self.browser.is_text_present('Why we deserve equal pay'))
        self.assertTrue(self.browser.is_text_present('Obviously'))

        # go to list & edit it
        self.browser.find_by_css(".document-link").first.click()
        self.browser.find_by_id('edit_document_main_button', wait_time=5).first.click()
        self.fill_out_add_or_edit_form(
            pairs={"name": "We deserve equal pay", "description": "Obviously!"}, close=True)
        self.assertTrue(self.browser.is_text_present('We deserve equal pay'))
        self.assertTrue(self.browser.is_text_present('Obviously!'))

        # edit content and discard
        self.browser.find_by_id('edit_content_start_button', wait_time=5).first.click()
        self.assertTrue(self.browser.is_text_present('hello'))  # default content in markdown editor
        self.browser.fill('document_content_textarea', "## A Header \n\n ## __Another__ Header")
        self.assertTrue(self.browser.is_text_present('Another Header'))
        self.browser.find_by_id('discard_content_edits', wait_time=5).first.click()
        self.assertFalse(self.browser.is_text_present('Another Header'))

        # edit content and save
        self.browser.find_by_id('edit_content_start_button', wait_time=5).first.click()
        self.assertTrue(self.browser.is_text_present('hello'))  # default content in markdown editor
        self.browser.fill('document_content_textarea', "## A Header \n\n ## __Another__ Header")
        self.assertTrue(self.browser.is_text_present('Another Header'))
        self.take_action()  # think it's the only action btn visible
        time.sleep(2)
        self.browser.find_by_id('discard_content_edits', wait_time=5).first.click()
        self.assertTrue(self.browser.is_text_present('Another Header'))
        found_textarea = self.browser.find_by_id('document_content_textarea')
        self.assertFalse(found_textarea)

        # full page view
        self.assertTrue(self.browser.is_text_present('Governance Forum'))  # in view with sidebar
        self.browser.find_by_id('document_fullpage', wait_time=5).first.click()
        self.assertFalse(self.browser.is_text_present('Governance Forum'))   # in view without sidebar
        self.assertTrue(self.browser.is_text_present('We deserve equal pay'))
        self.assertTrue(self.browser.is_text_present('Obviously!'))
        self.assertTrue(self.browser.is_text_present('A Header'))
        self.assertTrue(self.browser.is_text_present('Another Header'))


@skipIf("ForumsTestCase" in test_cases_to_skip, "")
class ForumsTestCase(BaseTestCase):

    def setUp(self):

        self.create_users()
        self.create_templates()
        self.actor = User.objects.first()
        self.client = Client(actor=self.actor)
        self.community = self.client.Community.create_community(name="USWNT")
        self.client.update_target_on_all(target=self.community)
        self.client.Community.add_members_to_community(member_pk_list=[user.pk for user in User.objects.all()])
        self.client.Community.add_role_to_community(role_name="forwards")
        pinoe = User.objects.get(username="meganrapinoe")
        press = User.objects.get(username="christenpress")
        heath = User.objects.get(username="tobinheath")
        self.client.Community.add_people_to_role(role_name="forwards", people_to_add=[pinoe.pk, press.pk, heath.pk])

    def test_create_forum(self):
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('add_forum_default_button').first.click()
        self.fill_out_add_or_edit_form(
            {'name': 'Strategy Sessions', 'description': 'A place to discuss strategy'}, close=True)
        time.sleep(1)
        self.browser.find_by_css(".forum-link", wait_time=5)[1].click()
        self.assertTrue(self.browser.is_text_present('Strategy Sessions'))
        self.assertTrue(self.browser.is_text_present('A place to discuss strategy'))

    def test_edit_forum(self):

        # Create forum
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('add_forum_default_button').first.click()
        self.fill_out_add_or_edit_form(
            {'name': 'Strategy Sessions', 'description': 'A place to discuss strategy'}, close=True)
        time.sleep(1)
        self.browser.find_by_css(".forum-link", wait_time=5)[1].click()

        # Edit forum
        self.browser.find_by_id("edit_forum_main_button", wait_time=5).last.click()
        self.fill_out_add_or_edit_form({"description": 'A place to make strategy'}, close=True)
        time.sleep(.25)
        self.assertFalse(self.browser.is_text_present('A place to discuss strategy'))
        self.assertTrue(self.browser.is_text_present('A place to make strategy'))

    def test_delete_forum(self):

        # Create forum
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('add_forum_default_button').first.click()
        self.fill_out_add_or_edit_form(
            {'name': 'Strategy Sessions', 'description': 'A place to discuss strategy'}, close=True)
        time.sleep(1)
        self.browser.find_by_css(".forum-link", wait_time=5)[1].click()

        # delete forum
        self.browser.find_by_id('delete_forum_button').first.click()
        time.sleep(2)
        self.take_action()
        time.sleep(2)
        self.assertFalse(self.browser.is_text_present('A place to discuss strategy'))

        # can't delete first (governance) forum
        self.browser.find_by_css(".forum-link").last.click()
        time.sleep(2)
        elements = self.browser.find_by_id('delete_forum_button')
        self.assertEquals(len(elements), 0)

    def test_add_edit_and_delete_post(self):

        # Create forum for post
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('add_forum_default_button').first.click()
        self.fill_out_add_or_edit_form(
            {'name': 'Strategy Sessions', 'description': 'A place to discuss strategy'}, close=True)
        self.browser.find_by_css(".forum-link", wait_time=5)[1].click()

        # Add post
        self.browser.find_by_id('add_post_default_button').first.click()
        self.fill_out_add_or_edit_form(
            {'title': 'I have an idea', 'content': "It's a good one"}, close=True)
        self.assertTrue(self.browser.is_text_present('I have an idea'))
        self.browser.find_by_css(".post-link", wait_time=5)[0].click()

        # Edit post
        self.browser.find_by_id('edit_post_main_button').first.click()
        self.fill_out_add_or_edit_form({'title': 'I have a great idea'}, close=True)
        self.assertTrue(self.browser.is_text_present('I have an idea'))
        time.sleep(2)
        self.browser.back()
        self.assertTrue(self.browser.is_text_present('I have a great idea'))

        # Delete post
        self.browser.find_by_css(".post-link").first.click()
        self.browser.find_by_id('delete_post_button').first.click()
        time.sleep(2)
        self.take_action()
        time.sleep(3)
        self.assertFalse(self.browser.is_text_present('I have a great idea'))

    def test_add_permission_to_forum(self):

        # Create forum
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('add_forum_default_button').first.click()
        self.fill_out_add_or_edit_form(
            {'name': 'Strategy Sessions', 'description': 'A place to discuss strategy'}, close=True)
        self.browser.find_by_css(".forum-link", wait_time=5)[1].click()

        # We start with only default permissions
        self.browser.find_by_id("forum_permissions", wait_time=5).first.click()
        time.sleep(3)
        permissions = [item.text for item in self.browser.find_by_css(".permissions-row")]
        self.assertEquals(len(permissions), 3)
        self.assertCountEqual(permissions, ["apply template", 'add comment', 'add post'])

        # For some reason, the rest of his *only* breaks when running in headless mode
        if settings.RUN_HEADLESS:
            return

        # Now we add a new permission
        self.browser.find_by_css('.add-permission', wait_time=5).first.click()
        time.sleep(3)
        self.select_from_multiselect("Edit forum", index=1)
        time.sleep(3)
        self.browser.find_by_id("add_audience", wait_time=5).first.click()
        time.sleep(1)
        self.select_from_multiselect("forwards", index=2)
        time.sleep(1)
        self.take_action()
        time.sleep(1)
        self.close_modal()
        time.sleep(3)
        permissions = [item.text for item in self.browser.find_by_css(".permissions-row")]
        self.assertCountEqual(permissions, ["apply template", 'add comment', 'add post', "edit forum"])


@skipIf("GroupBasicsTestCase" in test_cases_to_skip, "")
class GroupBasicsTestCase(BaseTestCase):

    def setUp(self):
        self.create_users()
        self.create_templates()
        self.actor = User.objects.first()
        self.client = Client(actor=self.actor)
        self.community = self.client.Community.create_community(name="USWNT")

    def test_create_group(self):
        self.login_user("meganrapinoe", "badlands2020")
        self.browser.visit(self.live_server_url + "/groups/list/")
        self.browser.links.find_by_text('Create a group').first.click()
        self.browser.fill('group_name', 'NWSL')
        self.browser.fill('group_description', 'For NWSL players')
        self.browser.find_by_id('start_from_scratch', wait_time=5).first.click()
        self.browser.find_by_id('create_group_button', wait_time=5).first.click()
        time.sleep(2)
        self.assertTrue(self.browser.is_text_present('edit', wait_time=5))  # shows we're on group detail page now
        self.assertTrue(self.browser.is_text_present("NWSL", wait_time=5))  # shows we're on newly created detail page now

    def test_add_members_to_group(self):

        # We start off with one member
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button', wait_time=5)[0].click()
        self.browser.find_by_id("customroles", wait_time=5).first.click()
        time.sleep(2)
        self.browser.find_by_id('members_member_count', wait_time=5)[0].scroll_to()
        self.assertEquals(self.browser.find_by_id('members_member_count', wait_time=5)[0].text, "1 people")
        self.browser.find_by_id("membership", wait_time=5).first.click()

        # Add a new member
        self.add_member("christenpress")
        time.sleep(3)
        names = [item.text for item in self.browser.find_by_css("span#current_member_list>span.badge", wait_time=5)]
        self.assertEquals(names, ["meganrapinoe", "christenpress"])
        self.close_modal()
        self.browser.find_by_id("customroles", wait_time=5).first.click()
        self.assertEquals(self.browser.find_by_id('members_member_count', wait_time=5).text, "2 people")

    def test_create_role(self):
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.add_role("forwards")
        time.sleep(4)
        self.close_modal()
        time.sleep(2)
        roles = [item.text for item in self.browser.find_by_css(".role_name_display")]
        self.assertEquals(roles, ["members", "forwards"])

    def test_add_members_to_role(self):

        # setup
        self.test_add_members_to_group()
        self.test_create_role()
        self.assertEquals(self.browser.find_by_id('forwards_member_count', wait_time=5).text, "0 people")

        # add person to role
        self.browser.find_by_id('forwards_add_members', wait_time=5).first.click()
        self.select_from_multiselect(selection="christenpress")
        self.assertEquals(["christenpress"], self.get_selected_in_multiselect())
        time.sleep(3)
        self.take_action()
        time.sleep(4)
        self.close_modal()
        time.sleep(2)
        self.assertEquals(self.browser.find_by_id('forwards_member_count', wait_time=5).text, "1 people")


@skipIf("ListTestCase" in test_cases_to_skip, "")
class ListTestCase(BaseTestCase):

    def setUp(self):

        # Basic setup
        self.create_users()
        self.create_templates()
        self.actor = User.objects.first()
        self.client = Client(actor=self.actor)
        self.community = self.client.Community.create_community(name="USWNT")
        self.client.update_target_on_all(target=self.community)
        self.client.Community.add_members_to_community(member_pk_list=[user.pk for user in User.objects.all()[:4]])
        self.client.Community.add_role_to_community(role_name="forwards")
        pinoe = User.objects.get(username="meganrapinoe")
        press = User.objects.get(username="christenpress")
        self.client.Community.add_people_to_role(role_name="forwards", people_to_add=[pinoe.pk, press.pk])

    def test_list_functionality(self):

        # create a list
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('add_list_default_button').first.click()
        self.fill_out_add_or_edit_form({
            "name": "Best NWSL Teams", 'description': "The best NWSL teams, in order of awesomeness"}, close=True)

        # edit name & description
        self.browser.find_by_id('link_to_list_0').first.click()
        self.browser.find_by_id('edit_list_main_button').first.click()
        self.fill_out_add_or_edit_form({
            "name": "Best NWSL Teams!", 'description': "The best NWSL teams, in order of awesomeness!"}, close=True)
        self.assertTrue(self.browser.is_text_present('The best NWSL teams, in order of awesomeness!'))

        # can add a new column that's required but no default value
        self.browser.find_by_id('add_column_button').first.click()
        self.browser.fill('columnName', "Team Name")
        self.browser.find_by_css(".custom-control-label").first.click()
        time.sleep(3)
        self.take_action()
        time.sleep(4)
        self.close_modal()
        self.assertTrue(self.browser.is_text_present('Team Name'))

        # add a row
        self.browser.find_by_id('add_row_button', wait_time=5).first.click()
        self.browser.fill('edit_Team Name', "Sky Blue FC")
        self.browser.find_by_id('submit_add_row').first.click()
        self.take_action()
        text = "You have successfully added row with content {'Team Name': 'Sky Blue FC'} to list."
        self.assertTrue(self.browser.is_text_present(text))
        self.close_modal()

        # can't add a new column that's required with no default value
        self.browser.find_by_id('add_column_button').first.click()
        self.browser.fill('columnName', "Currently Active")
        self.browser.find_by_css(".custom-control-label").first.click()
        time.sleep(3)
        self.take_action()
        time.sleep(3)
        text = "When adding a required column, you must supply a default value unless your list is empty"
        self.assertTrue(self.browser.is_text_present(text))

        # add a default value and save
        self.browser.fill('defaultValue', "Yes, currently active")
        self.take_action_and_close(
            response="You have successfully added column 'Currently Active' to list.")
        # row has the default value
        self.assertTrue(self.browser.is_text_present("Currently Active"))
        self.assertTrue(self.browser.is_text_present("Yes, currently active"))

        # editing a row works
        self.browser.find_by_id('edit_row_0').first.click()
        self.browser.fill('edit_Team Name', "NYNJ Gotham")
        self.browser.find_by_id('submit_edit_row').first.click()
        time.sleep(2)
        self.take_action_and_close(response="You have successfully edited row")
        time.sleep(2)
        self.assertEquals(len(self.browser.find_by_id('edit_Team Name')), 0)
        self.assertTrue(self.browser.is_text_present("NYNJ Gotham"))

        # editing a column name works
        self.browser.find_by_id('edit_column_Team Name').first.click()
        self.browser.fill('columnName', "Name of Team")
        self.take_action()
        time.sleep(2)
        self.take_action_and_close(response="You have successfully edited column 'Team Name'")
        time.sleep(2)
        self.assertTrue(self.browser.is_text_present("Name Of Team", wait_time=5))  # capitalized

        # editing a column to make it required means you have to set the default values
        self.browser.find_by_id('add_column_button').first.click()  # add a new column first
        self.browser.fill('columnName', "Number of Stars")
        self.take_action_and_close()

        self.browser.find_by_id('edit_column_Number Of Stars').first.click()  # now edit to make it required
        self.browser.find_by_css(".custom-control-label").first.click()
        self.take_action_and_close(
            response="When making a column required, you must supply a default value unless your list is empty")

        # delete row works
        self.browser.find_by_id('delete_row_0').first.click()
        self.take_action()
        time.sleep(3)
        self.assertFalse(self.browser.is_text_present("NYNJ Gotham"))

        # delete column works
        self.browser.find_by_id('edit_column_Number Of Stars').first.click()
        self.take_action_and_close(index=1)
        self.assertFalse(self.browser.is_text_present("Number of Stars"))

        # delete list works
        self.browser.find_by_id('delete_list_button').first.click()
        self.take_action()
        time.sleep(2)
        self.assertFalse(self.browser.is_text_present("Best NWSL Teams"))


@skipIf("MembershipTestCase" in test_cases_to_skip, "")
class MembershipTestCase(BaseTestCase):

    def setUp(self):
        # Basic setup
        self.create_users()
        self.create_templates()
        self.actor = User.objects.first()
        self.client = Client(actor=self.actor)
        self.community = self.client.Community.create_community(name="USWNT")
        self.client.update_target_on_all(target=self.community)
        self.client.Community.add_members_to_community(member_pk_list=[user.pk for user in User.objects.all()[:4]])
        self.client.Community.add_role_to_community(role_name="forwards")
        pinoe = User.objects.get(username="meganrapinoe")
        press = User.objects.get(username="christenpress")
        heath = User.objects.get(username="tobinheath")
        self.client.Community.add_people_to_role(role_name="forwards", people_to_add=[pinoe.pk, press.pk, heath.pk])

        # delete default membership permission
        from concord.permission_resources.models import PermissionsItem
        for permission in PermissionsItem.objects.all():
            if permission.change_type == Changes().Communities.AddMembers:
                permission.delete()

    def test_anyone_can_join(self):

        # we start with 4 members
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.check_member_count("4 people")

        # apply anyone can join template
        self.apply_membership_template("anyone_can_join")
        self.browser.reload()

        # check template was applied
        self.go_to_membership_settings()
        permissions = self.get_permissions(text=True)
        self.assertEquals(permissions, ["add members to community"])

        # random person can join
        self.login_user("midgepurce", "badlands2020")
        self.go_to_group("USWNT")
        time.sleep(1)
        self.browser.find_by_id("join_group_button", wait_time=5).first.click()
        time.sleep(2)
        self.take_action_and_close()
        time.sleep(2)

        # we should now have 5 members, not 4
        self.browser.find_by_id('governance_button', wait_time=5).first.click()
        self.browser.find_by_id("customroles", wait_time=5).first.click()
        self.browser.find_by_id('members_member_count', wait_time=5)[0].scroll_to()
        time.sleep(2)
        self.assertEquals(self.browser.find_by_id('members_member_count', wait_time=5)[0].text, "5 people")

    def test_invite_only(self):

        # we start with 4 members
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.check_member_count("4 people")

        # apply invite only template
        self.apply_membership_template("invite_only", supplied_role_field="forwards")
        self.browser.reload()

        # check that the template has been applied
        self.go_to_membership_settings()
        permissions = self.get_permissions(text=True)
        self.assertEquals(permissions, ["add members to community"])

        # Midge can't join
        self.login_user("midgepurce", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id("join_group_button", wait_time=5).first.click()
        time.sleep(2)
        self.check_if_take_action_disabled(should_be_disabled=True, alt_format=True)

        # but Christen, a forward, can invite her
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.add_member("midgepurce")
        time.sleep(3)
        self.assertTrue(self.browser.is_text_present(
            "There is a condition on your action which must be resolved before your action can be implemented.", wait_time=5))

        # Christen doesn't have permission to approve the invite
        self.click_through_link_in_response_and_open_condition()
        time.sleep(1)
        self.check_if_take_action_disabled(should_be_disabled=True)

        # Midge approves, and now there are 5 members
        self.login_user("midgepurce", "badlands2020")
        self.go_to_group("USWNT")
        self.go_to_most_recent_action_in_history_and_open_condition()   # will this go to the right place?
        self.approve_action()
        self.browser.reload()
        self.check_member_count("5 people")

    def test_anyone_can_request_to_join(self):

        # we start with 4 members
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.check_member_count("4 people")

        # apply anyone can request to join template
        time.sleep(3)
        self.apply_membership_template("anyone_can_request_to_join", supplied_role_field="forwards")
        self.browser.reload()

        # check template was applied
        self.go_to_membership_settings()
        permissions = self.get_permissions(text=True)
        self.assertEquals(permissions, ["add members to community"])

        # random person can request but they are not added yet
        self.login_user("midgepurce", "badlands2020")
        self.go_to_group("USWNT")
        time.sleep(1)
        self.browser.find_by_id("join_group_button", wait_time=5).first.click()
        time.sleep(2)
        self.take_action_and_close()
        time.sleep(2)
        self.check_member_count("4 people")

        # Christen Press, with role forwards, approves
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.go_to_most_recent_action_in_history_and_open_condition()
        self.approve_action()
        self.browser.reload()

        # we should now have 5 members, not 4
        self.check_member_count("5 people")


@skipIf("MultipleConditionsTestCase" in test_cases_to_skip, "")
class MultipleConditionsTestCase(BaseTestCase):

    def setUp(self):

        # Basic setup
        self.create_users()
        self.create_templates()
        self.actor = User.objects.first()
        self.client = Client(actor=self.actor)
        self.community = self.client.Community.create_community(name="USWNT")
        self.client.update_target_on_all(target=self.community)
        self.client.Community.add_members_to_community(member_pk_list=[user.pk for user in User.objects.all()[:4]])
        self.client.Community.add_role_to_community(role_name="forwards")
        pinoe = User.objects.get(username="meganrapinoe")
        press = User.objects.get(username="christenpress")
        heath = User.objects.get(username="tobinheath")
        self.client.Community.add_people_to_role(role_name="forwards", people_to_add=[pinoe.pk, press.pk, heath.pk])

        # Permission setup
        action, self.permission = self.client.PermissionResource.add_permission(
            change_type=Changes().Communities.AddRole, roles=["forwards"])

    def test_multiple_conditions(self):

        # add some conditions
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.go_to_edit_role("forwards")
        self.click_edit_perm_by_display_name("add role to community")
        time.sleep(2)
        self.add_condition_to_permission("ApprovalCondition", actor_choice="christenpress")
        time.sleep(2)
        self.add_condition_to_permission("ApprovalCondition", actor_choice="tobinheath")
        time.sleep(2)
        self.add_condition_to_permission("ApprovalCondition", actor_choice="cystaldunn")
        time.sleep(2)

        # delete first condition
        self.click_edit_cond_by_display_name("Approval Condition")
        self.browser.find_by_css(".remove-condition", wait_time=5).first.click()
        time.sleep(3)
        self.take_action()
        time.sleep(3)

        # edit both of last conditions because we can't be sure of order and want both to be tonin
        for index in [0, 1]:
            self.click_edit_cond_by_display_name("Approval Condition", index=index)
            element_containing_role_dropdown = self.browser.find_by_css(".permissionactorfield", wait_time=5)[0]
            names = self.get_selected_in_multiselect(search_within=element_containing_role_dropdown)
            if "tobinheath" not in names:
                self.select_from_multiselect("tobinheath", search_within=element_containing_role_dropdown)
                time.sleep(1)
                self.browser.find_by_css('.condition-ok').first.click()

        time.sleep(3)
        self.take_action()
        time.sleep(2)

        # take action to trigger the new conditions
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.add_role("midfielders")
        self.assertTrue(self.browser.is_text_present(
            'There is a condition on your action which must be resolved before your action can be implemented.',
            wait_time=5))

        # resolve each of the two remaining conditions
        self.login_user("tobinheath", "badlands2020")
        self.go_to_group("USWNT")
        self.go_to_most_recent_action_in_history_and_open_condition()
        self.assertTrue(self.browser.is_text_present('Please approve or reject this action.', wait_time=5))
        self.approve_action()
        time.sleep(2)
        self.close_modal()
        self.browser.find_by_css('.action-condition', wait_time=5)[1].click()
        self.approve_action()
        time.sleep(2)
        self.close_modal()

        # action implemented
        self.browser.reload()
        time.sleep(2)
        self.browser.find_by_id('governance_button', wait_time=5)[0].click()
        self.browser.find_by_id("customroles", wait_time=5).first.click()
        roles = [item.text for item in self.browser.find_by_css(".role_name_display", wait_time=5)]
        self.assertEquals(roles, ["members", "forwards", "midfielders"])


@skipIf("PermissionsTestCase" in test_cases_to_skip, "")
class PermissionsTestCase(BaseTestCase):

    def setUp(self):
        self.create_users()
        self.create_templates()
        self.actor = User.objects.first()
        self.client = Client(actor=self.actor)
        self.community = self.client.Community.create_community(name="USWNT")
        self.client.update_target_on_all(target=self.community)
        self.client.Community.add_members_to_community(member_pk_list=[user.pk for user in User.objects.all()])
        self.client.Community.add_role_to_community(role_name="forwards")
        pinoe = User.objects.get(username="meganrapinoe")
        press = User.objects.get(username="christenpress")
        heath = User.objects.get(username="tobinheath")
        self.client.Community.add_people_to_role(role_name="forwards", people_to_add=[pinoe.pk, press.pk, heath.pk])

    def test_add_permission_to_role(self):

        # we start with no permissions
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.go_to_edit_role("forwards")
        self.assertEquals(self.get_permissions(text=True), [])
        time.sleep(3)

        # For some reason, the rest of his *only* breaks when running in headless mode
        if settings.RUN_HEADLESS:
            return

        # add one
        self.browser.find_by_id('add_permission_button').first.click()
        self.select_from_multiselect("Remove members from community", index=1)
        time.sleep(1)
        self.browser.find_by_id("add_audience", wait_time=5).first.click()
        time.sleep(1)
        self.select_from_multiselect("forwards", index=2)
        time.sleep(1)
        self.take_action()
        time.sleep(3)
        self.browser.reload()
        self.go_to_edit_role("forwards")
        permissions = self.get_permissions(text=True)
        self.assertEquals(permissions, ["remove members from community"])

    def test_adding_permission_changes_site_behavior(self):

        if settings.RUN_HEADLESS:
            return

        # Add permission to role (same as above, minus asserts)
        self.test_add_permission_to_role()

        # Christen Press, a forward, can remove members
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.check_member_count("9 people")
        self.add_member("tobinheath", remove=True)
        time.sleep(2)
        self.browser.find_by_css(".close").first.click()  # close modal
        time.sleep(1)
        self.check_member_count("8 people")

        # Emily Sonnett, not a forward, cannot remove members
        self.login_user("emilysonnett", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button')[0].click()
        self.browser.find_by_id("membership", wait_time=5).first.click()
        self.browser.find_by_id('remove_members_display_button', wait_time=5).first.click()
        self.check_if_take_action_disabled(should_be_disabled=True)


@skipIf("TemplatesTestCase" in test_cases_to_skip, "")
class TemplatesTestCase(BaseTestCase):

    def setUp(self):
        # create group, add members, add roles, add members to role
        self.create_users()
        self.create_templates()
        self.actor = User.objects.first()
        self.client = Client(actor=self.actor)
        self.community = self.client.Community.create_community(name="USWNT")
        self.client.update_target_on_all(target=self.community)
        self.client.Community.add_members_to_community(member_pk_list=[user.pk for user in User.objects.all()])
        self.client.Community.add_role_to_community(role_name="forwards")
        pinoe = User.objects.get(username="meganrapinoe")
        press = User.objects.get(username="christenpress")
        heath = User.objects.get(username="tobinheath")
        self.client.Community.add_people_to_role(role_name="forwards", people_to_add=[pinoe.pk, press.pk, heath.pk])

    def test_apply_template_with_no_conditions(self):

        # we start off with one default permission
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.go_to_membership_settings()
        self.assertEquals(self.get_permissions(text=True), ["add members to community"])
        self.check_permission_table_cell(
            row="add_members_to_community", column="forwards", has_perm=False, has_info=False)

        self.browser.reload()
        # apply the template
        self.apply_membership_template("invite_only", supplied_role_field="forwards")
        time.sleep(5)

        # check that the template has been applied
        self.browser.reload()
        self.browser.find_by_id('governance_button', wait_time=5)[0].click()
        self.go_to_membership_settings()
        time.sleep(3)
        self.assertEquals(self.get_permissions(text=True), ["add members to community"])
        self.check_permission_table_cell(
            row="add_members_to_community", column="forwards", has_perm=True, has_info=True)

    def test_apply_template_with_condition(self):

        # we start off with one default permission
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.go_to_membership_settings()
        self.assertEquals(self.get_permissions(text=True), ["add members to community"])
        self.check_permission_table_cell(
            row="add_members_to_community", column="forwards", has_perm=False, has_info=False)

        # add a permission that gives the ability to apply templates, with a condition
        time.sleep(3)
        self.browser.find_by_id('add_permission_button', wait_time=5).first.click()
        time.sleep(2)
        self.select_from_multiselect("Apply template", index=1)
        time.sleep(2)
        self.browser.find_by_id("add_audience", wait_time=5).first.click()
        time.sleep(1)
        self.select_from_multiselect("forwards", index=2)
        time.sleep(1)
        self.take_action()
        time.sleep(4)
        self.add_condition_to_permission("ApprovalCondition", role_choice="forwards")
        time.sleep(2)

        # new user tries to apply a template
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        time.sleep(5)
        self.browser.find_by_id('governance_button', wait_time=5)[0].click()
        self.apply_membership_template("invite_only", supplied_role_field="forwards")
        time.sleep(5)
        self.assertTrue(self.browser.is_text_present("There is a condition"))

        # check that the template has not been applied and we've got the same permissions
        self.browser.reload()
        self.go_to_membership_settings()
        self.assertEquals(self.get_permissions(text=True), ["add members to community"])

        # log back in as pinoe, approve
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.go_to_most_recent_action_in_history_and_open_condition()
        self.approve_action()

        # check that the template has been applied now
        time.sleep(3)
        self.browser.reload()
        self.browser.find_by_id('governance_button', wait_time=5)[0].click()
        self.go_to_membership_settings()
        self.assertEquals(self.get_permissions(text=True), ["add members to community"])
        self.check_permission_table_cell(
            row="add_members_to_community", column="forwards", has_perm=True, has_info=True)


@skipIf("VotingConditionTestCase" in test_cases_to_skip, "")
class VotingConditionTestCase(BaseTestCase):

    def setUp(self):

        # create group, add members, add roles, add members to role
        self.create_users()
        self.create_templates()
        self.actor = User.objects.first()
        self.client = Client(actor=self.actor)
        self.community = self.client.Community.create_community(name="USWNT")
        self.client.update_target_on_all(target=self.community)
        self.client.Community.add_members_to_community(member_pk_list=[user.pk for user in User.objects.all()])
        self.client.Community.add_role_to_community(role_name="forwards")
        pinoe = User.objects.get(username="meganrapinoe")
        press = User.objects.get(username="christenpress")
        heath = User.objects.get(username="tobinheath")
        self.client.Community.add_people_to_role(role_name="forwards", people_to_add=[pinoe.pk, press.pk, heath.pk])

        # add permission & condition to permission
        action, self.permission = self.client.PermissionResource.add_permission(
            change_type=Changes().Communities.AddRole, roles=["forwards"]
        )
        perm_data = [{"permission_type": Changes().Conditionals.AddVote, "permission_roles": ["forwards"]}]
        self.client.Conditional.set_target(self.permission)
        self.client.Conditional.add_condition(condition_type="votecondition", permission_data=perm_data)

        # have person take action that triggers permission/condition
        self.client.Community.set_actor(heath)
        self.client.Community.add_role_to_community(role_name="midfielders")

    def test_yea_updates_vote_results(self):

        # User navigates to action history and votes yea
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.go_to_most_recent_action_in_history_and_open_condition()
        self.assertTrue(self.browser.is_text_present('The results so far are 0 yeas and 0 nays with 0 abstentions.'))
        self.assertTrue(self.browser.is_text_present('Please cast your vote'))
        self.browser.find_by_css("#btn-radios-1 > label:nth-child(1) > span").first.click()
        time.sleep(1)
        self.browser.find_by_id('save_vote_choice').first.click()
        time.sleep(1)
        self.assertTrue(self.browser.is_text_present('The results so far are 1 yeas and 0 nays with 0 abstentions.'))
        self.assertTrue(self.browser.is_text_present("Thank you for voting! No further action from you is needed."))

    def test_nay_updates_vote_results(self):

        # User navigates to action history and votes nay
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.go_to_most_recent_action_in_history_and_open_condition()
        self.assertTrue(self.browser.is_text_present('The results so far are 0 yeas and 0 nays with 0 abstentions.'))
        self.assertTrue(self.browser.is_text_present('Please cast your vote'))
        self.browser.find_by_css("#btn-radios-1 > label:nth-child(2) > span").first.click()
        time.sleep(1)
        self.browser.find_by_id('save_vote_choice').first.click()
        time.sleep(1)
        self.assertTrue(self.browser.is_text_present('The results so far are 0 yeas and 1 nays with 0 abstentions.'))
        self.assertTrue(self.browser.is_text_present("Thank you for voting! No further action from you is needed."))

    def test_abstain_updates_vote_results(self):

        # User navigates to action history and votes nay
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.go_to_most_recent_action_in_history_and_open_condition()
        self.assertTrue(self.browser.is_text_present('The results so far are 0 yeas and 0 nays with 0 abstentions.'))
        self.assertTrue(self.browser.is_text_present('Please cast your vote'))
        self.browser.find_by_css("#btn-radios-1 > label:nth-child(3) > span").first.click()
        time.sleep(1)
        self.browser.find_by_id('save_vote_choice').first.click()
        time.sleep(1)
        self.assertTrue(self.browser.is_text_present('The results so far are 0 yeas and 0 nays with 1 abstentions.'))
        self.assertTrue(self.browser.is_text_present("Thank you for voting! No further action from you is needed."))

    def test_person_without_permission_to_approve_cant_vote(self):

        self.login_user("emilysonnett", "badlands2020")
        self.go_to_group("USWNT")
        self.go_to_most_recent_action_in_history_and_open_condition()
        self.assertTrue(self.browser.is_text_present('You are not eligible to vote.'))
