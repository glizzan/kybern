import time, os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from splinter import Browser
from django.conf import settings
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from django.contrib.auth.models import User
from concord.utils.helpers  import Changes, Client
from groups.models import Forum
from concord.actions.models import TemplateModel

settings.DEBUG = True
chrome_options = webdriver.ChromeOptions()
run_headless = True

if os.environ.get("GITHUB_ACTIONS") or run_headless:
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1200,1100')


class BaseTestCase(StaticLiveServerTestCase):
    """BaseTestCase contains all setup & teardown used universally by tests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = Browser('chrome', options=chrome_options)

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

    def login_user(self, username, password):
        self.browser.visit(self.live_server_url + "/login/")
        self.browser.fill('username', username)
        self.browser.fill('password', password)
        self.browser.find_by_id('submit_login').first.click()

    def get_selected_in_multiselect(self):
        names = []
        for item in self.browser.find_by_css(".multiselect__tag"):
            names.append(item.text)
        return names

    def delete_selected_in_multiselect(self, username):
        for item in self.browser.find_by_css(".multiselect__tag"):
            if item.text == username:
                item.find_by_css(".multiselect__tag-icon").first.click()
                return True
        return False

    def select_from_multiselect(self, selection, element_css=".multiselect__element", search_within=None):
        """Helper method to select options given the custom interface vue-multiselect provides."""
        base = search_within if search_within else self.browser
        base.find_by_css(".multiselect__select").first.click()
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
        self.assertTrue(self.browser.is_text_present('Your Profile'))
        self.assertTrue(self.browser.is_text_present('username: meganrapinoe'))


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
        self.assertTrue(self.browser.is_text_present('edit group', wait_time=5))  # shows we're on group detail page now
        self.assertTrue(self.browser.is_text_present("NWSL's Forums", wait_time=5))  # shows we're on newly created detail page now

    def test_add_members_to_group(self):
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button', wait_time=5)[0].click()
        self.browser.find_by_id('members_member_count', wait_time=5)[0].scroll_to()
        self.assertEquals(self.browser.find_by_id('members_member_count', wait_time=5)[0].text, "1 people")
        self.browser.find_by_id('group_membership_display_button', wait_time=5).first.click()
        time.sleep(.5)
        names = [item.text for item in self.browser.find_by_css("span#current_member_list>span.badge", wait_time=5)]
        self.assertEquals(names, ["meganrapinoe"])
        self.browser.find_by_id('add_member_button', wait_time=5).first.click()
        time.sleep(.25)
        self.select_from_multiselect(selection="christenpress")
        time.sleep(.5)
        self.assertEquals(["christenpress"], self.get_selected_in_multiselect())
        self.browser.find_by_id('save_add_member_button', wait_time=5).first.click()
        time.sleep(.5)
        names = [item.text for item in self.browser.find_by_css("span#current_member_list>span.badge", wait_time=5)]
        self.assertEquals(names, ["meganrapinoe", "christenpress"])
        self.browser.find_by_css(".close", wait_time=5).first.click()  # close modal
        self.assertEquals(self.browser.find_by_id('members_member_count', wait_time=5).text, "2 people")

    def test_create_role(self):
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button', wait_time=5)[0].click()
        self.browser.find_by_id('add_role_button', wait_time=5)[0].scroll_to()
        self.browser.find_by_id('add_role_button', wait_time=5).first.click()
        self.browser.fill('role_name', 'forwards')
        self.browser.find_by_id('save_role_button', wait_time=5).first.click()
        self.browser.find_by_css(".close", wait_time=5).first.click()  # close modal
        time.sleep(.5)
        roles = [item.text for item in self.browser.find_by_css(".role_name_display")]
        self.assertEquals(roles, ["members", "forwards"])

    def test_add_members_to_role(self):
        self.test_add_members_to_group()
        self.test_create_role()
        self.assertEquals(self.browser.find_by_id('forwards_member_count', wait_time=5).text, "0 people")
        self.browser.find_by_id('forwards_changemembers', wait_time=5).first.click()
        self.select_from_multiselect(selection="christenpress")
        self.assertEquals(["christenpress"], self.get_selected_in_multiselect())
        self.browser.find_by_id('save_member_changes', wait_time=5).first.click()
        self.browser.find_by_css(".close", wait_time=5).first.click()  # close modal
        self.assertEquals(self.browser.find_by_id('forwards_member_count', wait_time=5).text, "1 people")


class PermissionsTestCase(BaseTestCase):

    def setUp(self):
        self.create_users()
        self.create_templates()
        self.actor = User.objects.first()
        self.client = Client(actor=self.actor)
        self.community = self.client.Community.create_community(name="USWNT")
        self.client.update_target_on_all(target=self.community)
        self.client.Community.add_members(member_pk_list=[user.pk for user in User.objects.all()])
        self.client.Community.add_role(role_name="forwards")
        pinoe = User.objects.get(username="meganrapinoe")
        press = User.objects.get(username="christenpress")
        heath = User.objects.get(username="tobinheath")
        self.client.Community.add_people_to_role(role_name="forwards", people_to_add=[pinoe.pk, press.pk, heath.pk])

    def test_add_permission_to_role(self):
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button')[0].click()
        self.browser.find_by_id('forwards_editrole')[0].scroll_to()
        self.browser.find_by_id('forwards_editrole').first.click()
        permissions = [item.text for item in self.browser.find_by_css(".permission-display")]
        self.assertEquals(permissions, [])
        self.browser.find_by_id('add_permission_button').first.click()
        self.select_from_multiselect("Remove members")
        self.browser.find_by_id('save_permission_button').first.click()
        time.sleep(.25)
        permissions = [item.text for item in self.browser.find_by_css(".permission-display")]
        self.assertEquals(permissions, ["those with role forwards have permission to remove members from community"])

    def test_adding_permission_changes_site_behavior(self):

        # Add permission to role (same as above, minus asserts)
        self.test_add_permission_to_role()

        # Christen Press, a forward, can remove members
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button')[0].click()
        self.browser.find_by_id('members_member_count').scroll_to()
        self.assertEquals(self.browser.find_by_id('members_member_count').text, "9 people")
        self.browser.find_by_id('group_membership_display_button').first.click()
        time.sleep(.25)
        self.browser.find_by_id('remove_member_button').first.click()
        time.sleep(.25)
        self.select_from_multiselect(selection="tobinheath")
        time.sleep(.25)
        self.assertEquals(["tobinheath"], self.get_selected_in_multiselect())
        self.browser.find_by_id('save_remove_member_button').first.click()
        time.sleep(.25)
        self.browser.find_by_css(".close").first.click()  # close modal
        time.sleep(.5)
        self.assertEquals(self.browser.find_by_id('members_member_count').text, "8 people")

        # Emily Sonnett, not a forward, cannot remove members
        self.login_user("emilysonnett", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button')[0].click()
        self.browser.find_by_id('group_membership_display_button').first.click()
        time.sleep(.25)
        self.assertEquals(len(self.browser.find_by_id('remove_member_button')), 0)


class ActionsTestCase(BaseTestCase):

    def setUp(self):
        self.create_users()
        self.create_templates()
        self.actor = User.objects.first()
        self.client = Client(actor=self.actor)
        self.community = self.client.Community.create_community(name="USWNT")
        self.client.update_target_on_all(target=self.community)
        self.client.Community.add_members(member_pk_list=[user.pk for user in User.objects.all()])

    def test_taking_action_generates_action(self):

        # Add role
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button')[0].click()
        self.browser.find_by_css("#add_role_button")[0].scroll_to()
        self.browser.find_by_id('add_role_button').first.click()
        self.browser.fill('role_name', 'forwards')
        self.browser.find_by_id('save_role_button').first.click()
        self.browser.find_by_css(".close").first.click()  # close modal

        # Check for action in action history
        self.browser.find_by_id('group_history_button')[0].click()
        self.assertTrue(self.browser.is_text_present('meganrapinoe added role forwards'))


class ActionConditionsTestCase(BaseTestCase):

    def setUp(self):

        # Basic setup
        self.create_users()
        self.create_templates()
        self.actor = User.objects.first()
        self.client = Client(actor=self.actor)
        self.community = self.client.Community.create_community(name="USWNT")
        self.client.update_target_on_all(target=self.community)
        self.client.Community.add_members(member_pk_list=[user.pk for user in User.objects.all()])
        self.client.Community.add_role(role_name="forwards")
        pinoe = User.objects.get(username="meganrapinoe")
        press = User.objects.get(username="christenpress")
        heath = User.objects.get(username="tobinheath")
        self.client.Community.add_people_to_role(role_name="forwards", people_to_add=[pinoe.pk, press.pk, heath.pk])

        # Permission setup
        action, self.permission = self.client.PermissionResource.add_permission(
            permission_type=Changes().Communities.AddRole, permission_roles=["forwards"])

    def test_adding_condition_to_permission_generates_condition(self):

        # Pinoe adds condition to permission
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button', wait_time=5)[0].click()
        self.browser.find_by_id('forwards_editrole', wait_time=5)[0].scroll_to()
        self.browser.find_by_id('forwards_editrole', wait_time=5).first.click()
        perm_element = self.browser.find_by_text("those with role forwards have permission to add role to community", wait_time=5)
        cond_id = "_".join(["condition"] + perm_element[0]["id"].split("_")[1:])
        condition_element = self.browser.find_by_id(cond_id, wait_time=5).first
        condition_element.find_by_text("add condition", wait_time=5).first.click()
        self.browser.find_by_id("new_condition", wait_time=5).first.click()
        self.browser.select("condition_select", "VoteCondition")
        element_containing_role_dropdown = self.browser.find_by_css(".permissionrolefield", wait_time=5)[0]
        self.select_from_multiselect("forwards", search_within=element_containing_role_dropdown)
        self.browser.find_by_id('save_condition_button', wait_time=5).first.click()
        time.sleep(.3)

        # Someone with the permission tries to take action (use asserts to check for condition error text)
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button', wait_time=5)[0].click()
        self.browser.find_by_id('add_role_button', wait_time=5).first.click()
        self.browser.fill('role_name', 'midfielders')
        self.browser.find_by_id('save_role_button', wait_time=5).first.click()
        self.assertTrue(self.browser.is_text_present(
            'There is a condition on your action which must be resolved before your action can be implemented.', wait_time=5))

        # Click through to condition
        self.browser.find_by_id('condition_link', wait_time=5)[0].click()
        self.assertTrue(self.browser.is_text_present('Please cast your vote', wait_time=5))


class ApprovalConditionsTestCase(BaseTestCase):

    def setUp(self):

        # create group, add members, add roles, add members to role
        self.create_users()
        self.create_templates()
        self.actor = User.objects.first()
        self.client = Client(actor=self.actor)
        self.community = self.client.Community.create_community(name="USWNT")
        self.client.update_target_on_all(target=self.community)
        self.client.Community.add_members(member_pk_list=[user.pk for user in User.objects.all()])
        self.client.Community.add_role(role_name="forwards")
        pinoe = User.objects.get(username="meganrapinoe")
        press = User.objects.get(username="christenpress")
        heath = User.objects.get(username="tobinheath")
        self.client.Community.add_people_to_role(role_name="forwards", people_to_add=[pinoe.pk, press.pk, heath.pk])

        # add permission & condition to permission
        action, self.permission = self.client.PermissionResource.add_permission(
            permission_type=Changes().Communities.AddRole, permission_roles=["forwards"])
        perm_data = [
            {"permission_type": Changes().Conditionals.Approve, "permission_roles": ["forwards"]},
            {"permission_type": Changes().Conditionals.Reject, "permission_roles": ["forwards"]}
        ]
        self.client.Conditional.set_target(self.permission)
        self.client.Conditional.add_condition(condition_type="approvalcondition", permission_data=perm_data)

        # have person take action that triggers permission/condition
        self.client.Community.set_actor(heath)
        self.client.Community.add_role(role_name="midfielders")

    def test_approve_implements_action(self):

        # User navigates to action history and approves action
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('group_history_button')[0].click()
        self.assertTrue(self.browser.is_text_present('tobinheath asked to add role midfielders'))
        self.browser.find_by_css(".action-link-button")[0].click()
        self.assertTrue(self.browser.is_text_present('Please approve or reject this action.'))
        self.browser.find_by_css("#btn-radios-1 > label:nth-child(1) > span").first.click()
        time.sleep(.25)
        self.browser.find_by_id('save_approve_choice').first.click()
        time.sleep(.25)
        text = "You have approved tobinheath's action. Nothing further is needed from you."
        self.assertTrue(self.browser.is_text_present(text))

        # Check action is implemented
        self.browser.back()
        time.sleep(.25)
        css_str = "#action_history_table_element > tbody > tr:nth-child(1)"
        self.assertTrue("implemented" in self.browser.find_by_css(css_str)[0].text)

    def test_reject_rejects_action(self):

        # User navigates to action history and approves action
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('group_history_button')[0].click()
        self.assertTrue(self.browser.is_text_present('tobinheath asked to add role midfielders'))
        self.browser.find_by_css(".action-link-button")[0].click()
        self.assertTrue(self.browser.is_text_present('Please approve or reject this action.'))
        self.browser.find_by_css("#btn-radios-1 > label:nth-child(2) > span").first.click()
        self.browser.find_by_id('save_approve_choice').first.click()
        time.sleep(.25)
        text = "You have rejected tobinheath's action. Nothing further is needed from you."
        self.assertTrue(self.browser.is_text_present(text))

        # Check action is rejected
        self.browser.back()
        time.sleep(.25)
        css_str = "#action_history_table_element > tbody > tr:nth-child(1)"
        self.assertTrue("rejected" in self.browser.find_by_css(css_str)[0].text)

    def test_person_without_permission_to_approve_cant_approve(self):
        self.login_user("emilysonnett", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('group_history_button')[0].click()
        self.assertTrue(self.browser.is_text_present('tobinheath asked to add role midfielders'))
        self.browser.find_by_css(".action-link-button")[0].click()
        self.assertTrue(self.browser.is_text_present('You do not have permission to approve or reject this action.'))


class VotingConditionTestCase(BaseTestCase):

    def setUp(self):

        # create group, add members, add roles, add members to role
        self.create_users()
        self.create_templates()
        self.actor = User.objects.first()
        self.client = Client(actor=self.actor)
        self.community = self.client.Community.create_community(name="USWNT")
        self.client.update_target_on_all(target=self.community)
        self.client.Community.add_members(member_pk_list=[user.pk for user in User.objects.all()])
        self.client.Community.add_role(role_name="forwards")
        pinoe = User.objects.get(username="meganrapinoe")
        press = User.objects.get(username="christenpress")
        heath = User.objects.get(username="tobinheath")
        self.client.Community.add_people_to_role(role_name="forwards", people_to_add=[pinoe.pk, press.pk, heath.pk])

        # add permission & condition to permission
        action, self.permission = self.client.PermissionResource.add_permission(
            permission_type=Changes().Communities.AddRole, permission_roles=["forwards"]
        )
        perm_data = [{"permission_type": Changes().Conditionals.AddVote, "permission_roles": ["forwards"]}]
        self.client.Conditional.set_target(self.permission)
        self.client.Conditional.add_condition(condition_type="votecondition", permission_data=perm_data)

        # have person take action that triggers permission/condition
        self.client.Community.set_actor(heath)
        self.client.Community.add_role(role_name="midfielders")

    def test_yea_updates_vote_results(self):

        # User navigates to action history and votes yea
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('group_history_button')[0].click()
        self.assertTrue(self.browser.is_text_present('tobinheath asked to add role midfielders'))
        self.browser.find_by_css(".action-link-button")[0].click()
        self.assertTrue(self.browser.is_text_present('The results so far are 0 yeas and 0 nays with 0 abstentions.'))
        self.assertTrue(self.browser.is_text_present('Please cast your vote'))
        self.browser.find_by_css("#btn-radios-1 > label:nth-child(1) > span").first.click()
        time.sleep(.25)
        self.browser.find_by_id('save_vote_choice').first.click()
        time.sleep(.25)
        self.assertTrue(self.browser.is_text_present('The results so far are 1 yeas and 0 nays with 0 abstentions.'))
        self.assertTrue(self.browser.is_text_present("Thank you for voting! No further action from you is needed."))

    def test_nay_updates_vote_results(self):

        # User navigates to action history and votes nay
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('group_history_button')[0].click()
        self.assertTrue(self.browser.is_text_present('tobinheath asked to add role midfielders'))
        self.browser.find_by_css(".action-link-button")[0].click()
        self.assertTrue(self.browser.is_text_present('The results so far are 0 yeas and 0 nays with 0 abstentions.'))
        self.assertTrue(self.browser.is_text_present('Please cast your vote'))
        self.browser.find_by_css("#btn-radios-1 > label:nth-child(2) > span").first.click()
        time.sleep(.25)
        self.browser.find_by_id('save_vote_choice').first.click()
        time.sleep(.25)
        self.assertTrue(self.browser.is_text_present('The results so far are 0 yeas and 1 nays with 0 abstentions.'))
        self.assertTrue(self.browser.is_text_present("Thank you for voting! No further action from you is needed."))

    def test_abstain_updates_vote_results(self):

        # User navigates to action history and votes nay
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('group_history_button')[0].click()
        self.assertTrue(self.browser.is_text_present('tobinheath asked to add role midfielders'))
        self.browser.find_by_css(".action-link-button")[0].click()
        self.assertTrue(self.browser.is_text_present('The results so far are 0 yeas and 0 nays with 0 abstentions.'))
        self.assertTrue(self.browser.is_text_present('Please cast your vote'))
        self.browser.find_by_css("#btn-radios-1 > label:nth-child(3) > span").first.click()
        time.sleep(.25)
        self.browser.find_by_id('save_vote_choice').first.click()
        time.sleep(.25)
        self.assertTrue(self.browser.is_text_present('The results so far are 0 yeas and 0 nays with 1 abstentions.'))
        self.assertTrue(self.browser.is_text_present("Thank you for voting! No further action from you is needed."))

    def test_person_without_permission_to_approve_cant_vote(self):

        self.login_user("emilysonnett", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('group_history_button')[0].click()
        self.assertTrue(self.browser.is_text_present('tobinheath asked to add role midfielders'))
        self.browser.find_by_css(".action-link-button")[0].click()
        self.assertTrue(self.browser.is_text_present('You are not eligible to vote.'))


class ConsensusConditionTestCase(BaseTestCase):

    def setUp(self):
        self.create_users()
        self.create_templates()
        self.actor = User.objects.first()
        self.client = Client(actor=self.actor)
        self.community = self.client.Community.create_community(name="USWNT")
        self.client.update_target_on_all(target=self.community)
        self.client.Community.add_members(member_pk_list=[user.pk for user in User.objects.all()])
        self.client.Community.add_role(role_name="forwards")
        self.client.Community.add_role(role_name="defense")
        self.client.Community.add_role(role_name="captains")
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
            permission_type=Changes().Communities.AddRole, permission_roles=["defense"]
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
        self.browser.find_by_id('governance_button')[0].click()
        self.browser.find_by_id('add_role_button')[0].scroll_to()
        self.browser.find_by_id('add_role_button').first.click()
        self.browser.fill('role_name', 'midfielders')
        self.browser.find_by_id('save_role_button').first.click()
        self.assertTrue(self.browser.is_text_present(
            "There is a condition on your action which must be resolved before your action can be implemented."))

        self.browser.back()
        self.browser.find_by_id('group_history_button').first.click()
        self.browser.find_by_text("link").first.click()
        self.assertTrue(self.browser.is_text_present(
            'The discussion cannot be resolved until the minimum duration of 2 days has passed.'))
        self.assertTrue(self.browser.is_text_present('You are not a participant in this consensus decision.'))

    def test_loose_consensus_condition(self):

        # set up permission & condition
        action, self.permission = self.client.PermissionResource.add_permission(
            permission_type=Changes().Communities.AddRole, permission_roles=["defense"]
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
        self.browser.find_by_id('governance_button')[0].click()
        self.browser.find_by_id('add_role_button')[0].scroll_to()
        self.browser.find_by_id('add_role_button').first.click()
        self.browser.fill('role_name', 'midfielders')
        self.browser.find_by_id('save_role_button').first.click()
        time.sleep(.5)
        self.assertTrue(self.browser.is_text_present(
            "There is a condition on your action which must be resolved before your action can be implemented."))
        self.browser.back()
        self.browser.find_by_id('group_history_button').first.click()
        self.browser.find_by_text("link").first.click()
        self.assertTrue(self.browser.is_text_present(
            'The minimum duration of has passed. If the discussion was resolved right now, the result would be: rejected.'))

        # Crystal adds support, it is now passing
        self.assertEquals(self.browser.find_by_id('support_names').first.value, "")
        self.browser.find_by_id('user_response_radio_buttons')[0].scroll_to()
        self.browser.find_by_css("#user_response_radio_buttons > label:first-child").first.click()
        self.browser.find_by_id('submit_response').first.click()
        time.sleep(.5)
        self.assertEquals(self.browser.find_by_id('support_names').first.value, "crystaldunn")
        self.assertTrue(self.browser.is_text_present(
            'The minimum duration of has passed. If the discussion was resolved right now, the result would be: approved.'))

        # another player adds block, is no longer passing
        self.login_user("tobinheath", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('group_history_button').first.click()
        self.browser.find_by_text("link").first.click()
        self.browser.find_by_id('user_response_radio_buttons')[0].scroll_to()
        self.browser.find_by_css("#user_response_radio_buttons > label:nth-child(4)").first.click()
        self.browser.find_by_id('submit_response').first.click()
        time.sleep(.5)
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
        self.browser.find_by_id('group_history_button').first.click()
        self.browser.find_by_text("link").first.click()
        self.browser.find_by_id('resolve_button').first.click()
        self.assertTrue(self.browser.is_text_present('The condition was resolved with resolution approved. Your response was no response.'))

        # change is implemented
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button').first.click()
        roles = [item.text for item in self.browser.find_by_css(".role_name_display")]
        self.assertEquals(roles, ["members", "forwards", "defense", "captains", "midfielders"])

    def test_strict_consensus_condition(self):

        # set up permission & condition
        action, self.permission = self.client.PermissionResource.add_permission(
            permission_type=Changes().Communities.AddRole, permission_roles=["defense"]
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
        self.browser.find_by_id('governance_button')[0].click()
        self.browser.find_by_id('add_role_button')[0].scroll_to()
        self.browser.find_by_id('add_role_button').first.click()
        self.browser.fill('role_name', 'midfielders')
        self.browser.find_by_id('save_role_button').first.click()
        self.assertTrue(self.browser.is_text_present(
            "There is a condition on your action which must be resolved before your action can be implemented."))
        self.browser.back()
        self.browser.find_by_id('group_history_button').first.click()
        self.browser.find_by_text("link").first.click()
        self.assertTrue(self.browser.is_text_present(
            'The minimum duration of has passed. If the discussion was resolved right now, the result would be: rejected.'))

        # players respond, but it won't pass until all have responded so it keeps saying it would be rejected

        self.assertEquals(self.browser.find_by_id('support_names').first.value, "")
        self.browser.find_by_id('user_response_radio_buttons')[0].scroll_to()
        self.browser.find_by_css("#user_response_radio_buttons > label:first-child").first.click()
        self.browser.find_by_id('submit_response').first.click()
        time.sleep(.5)
        self.assertEquals(self.browser.find_by_id('support_names').first.value, "crystaldunn")
        self.assertTrue(self.browser.is_text_present(
            'The minimum duration of has passed. If the discussion was resolved right now, the result would be: rejected.'))

        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('group_history_button').first.click()
        self.browser.find_by_text("link").first.click()
        self.browser.find_by_id('user_response_radio_buttons')[0].scroll_to()
        self.browser.find_by_css("#user_response_radio_buttons > label:first-child").first.click()
        self.browser.find_by_id('submit_response').first.click()
        time.sleep(.5)
        self.assertEquals(self.browser.find_by_id('support_names').first.value, "christenpress, crystaldunn")
        self.assertTrue(self.browser.is_text_present(
            'The minimum duration of has passed. If the discussion was resolved right now, the result would be: rejected.'))

        # resolves with not enough people responding so rejected
        self.browser.find_by_id('resolve_button').first.click()
        self.assertTrue(self.browser.is_text_present('The condition was resolved with resolution rejected. Your response was support.'))


class ForumsTestCase(BaseTestCase):

    def setUp(self):

        self.create_users()
        self.create_templates()
        self.actor = User.objects.first()
        self.client = Client(actor=self.actor)
        self.community = self.client.Community.create_community(name="USWNT")
        self.client.update_target_on_all(target=self.community)
        self.client.Community.add_members(member_pk_list=[user.pk for user in User.objects.all()])
        self.client.Community.add_role(role_name="forwards")
        pinoe = User.objects.get(username="meganrapinoe")
        press = User.objects.get(username="christenpress")
        heath = User.objects.get(username="tobinheath")
        self.client.Community.add_people_to_role(role_name="forwards", people_to_add=[pinoe.pk, press.pk, heath.pk])

    def test_create_forum(self):
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('new_forum_button').first.click()
        self.browser.fill('forum_name', 'Strategy Sessions')
        self.browser.fill('forum_description', 'A place to discuss strategy')
        self.browser.find_by_id('add_forum_button').first.click()
        time.sleep(1)
        self.browser.find_by_css(".close").first.click()  # close modal
        self.assertTrue(self.browser.is_text_present('Strategy Sessions'))
        self.assertTrue(self.browser.is_text_present('A place to discuss strategy'))

    def test_edit_forum(self):

        # Create forum
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('new_forum_button').first.click()
        self.browser.fill('forum_name', 'Strategy Sessions')
        self.browser.fill('forum_description', 'A place to discuss strategy')
        self.browser.find_by_id('add_forum_button').first.click()
        self.browser.find_by_css(".close").first.click()  # close modal

        # Edit forum
        time.sleep(.25)
        self.browser.find_by_css(".forum-description").last.click()
        self.browser.find_by_id("edit_forum_button").first.click()
        self.browser.fill('forum_description', 'A place to make strategy')
        self.browser.find_by_id('edit_forum_save_button').first.click()
        self.browser.find_by_css(".close").first.click()  # close modal
        time.sleep(.25)
        self.assertFalse(self.browser.is_text_present('A place to discuss strategy'))
        self.assertTrue(self.browser.is_text_present('A place to make strategy'))

    def test_delete_forum(self):

        # Create forum
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('new_forum_button').first.click()
        self.browser.fill('forum_name', 'Strategy Sessions')
        self.browser.fill('forum_description', 'A place to discuss strategy')
        self.browser.find_by_id('add_forum_button').first.click()
        time.sleep(.5)
        self.browser.find_by_css(".close").first.click()  # close modal

        # can't delete first (governance) forum
        self.browser.find_by_css(".forum-description").first.click()
        self.assertFalse(self.browser.is_text_present('delete forum'))
        self.browser.back()

        # delete forum
        self.browser.find_by_css(".forum-description").last.click()
        time.sleep(.5)
        self.browser.find_by_id('delete_forum_button').first.click()
        time.sleep(.5)
        self.assertFalse(self.browser.is_text_present('A place to discuss strategy'))

    def test_add_edit_and_delete_post(self):

        # Create forum for post
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('new_forum_button').first.click()
        self.browser.fill('forum_name', 'Strategy Sessions')
        self.browser.fill('forum_description', 'A place to discuss strategy')
        self.browser.find_by_id('add_forum_button').first.click()
        self.browser.find_by_css(".close").first.click()  # close modal
        self.browser.find_by_css(".forum-description").first.click()

        # Add post
        self.browser.find_by_id('add_post_button').first.click()
        self.browser.fill('post_title', 'I have an idea')
        self.browser.fill('post_content', "It's a good one")
        self.browser.find_by_id('add_post_save_button').first.click()
        self.assertTrue(self.browser.is_text_present('I have an idea'))

        # Edit post
        self.browser.find_by_css(".post-content").first.click()
        self.browser.find_by_id('edit_post_button').first.click()
        time.sleep(.5)
        self.browser.fill('post_title', 'I have a great idea')
        self.browser.find_by_id('edit_post_save_button').first.click()
        time.sleep(.25)
        self.assertTrue(self.browser.is_text_present('I have a great idea'))

        # Delete post
        self.browser.find_by_id('delete_post_button').first.click()
        time.sleep(.5)
        self.assertFalse(self.browser.is_text_present('I have a great idea'))

    def test_add_permission_to_forum(self):

        # Create forum
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('new_forum_button').first.click()
        self.browser.fill('forum_name', 'Strategy Sessions')
        self.browser.fill('forum_description', 'A place to discuss strategy')
        self.browser.find_by_id('add_forum_button').first.click()
        self.browser.find_by_css(".close").first.click()  # close modal
        self.browser.find_by_css(".forum-description").first.click()
        time.sleep(.25)

        # Add permissions - we start with only default permissions, but then have one more
        self.browser.find_by_id("forum_permissions_button").first.click()
        permissions = [item.text for item in self.browser.find_by_css(".permission-display")]
        self.assertCountEqual(permissions, ['those with role members have permission to add comment',
                                            'those with role members have permission to add a post'])
        self.browser.find_by_id('add_permission_button').first.click()
        self.select_from_multiselect("Edit a forum")
        time.sleep(.25)
        element_containing_role_dropdown = self.browser.find_by_css(".permissionrolefield")[0]
        self.select_from_multiselect("forwards", search_within=element_containing_role_dropdown)
        self.browser.find_by_id('save_permission_button').first.click()
        time.sleep(.25)
        permissions = [item.text for item in self.browser.find_by_css(".permission-display")]
        self.assertCountEqual(permissions, ['those with role forwards have permission to edit a forum',
                                            'those with role members have permission to add comment',
                                            'those with role members have permission to add a post'])


class TemplatesTestCase(BaseTestCase):

    def setUp(self):
        # create group, add members, add roles, add members to role
        self.create_users()
        self.create_templates()
        self.actor = User.objects.first()
        self.client = Client(actor=self.actor)
        self.community = self.client.Community.create_community(name="USWNT")
        self.client.update_target_on_all(target=self.community)
        self.client.Community.add_members(member_pk_list=[user.pk for user in User.objects.all()])
        self.client.Community.add_role(role_name="forwards")
        pinoe = User.objects.get(username="meganrapinoe")
        press = User.objects.get(username="christenpress")
        heath = User.objects.get(username="tobinheath")
        self.client.Community.add_people_to_role(role_name="forwards", people_to_add=[pinoe.pk, press.pk, heath.pk])

    def test_apply_template_with_no_conditions(self):

        # apply the template
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button', wait_time=5).first.click()
        self.browser.find_by_id('group_membership_settings_button', wait_time=5).first.click()
        self.browser.find_by_id('membership_templates_link', wait_time=5).first.click()
        self.browser.find_by_id('select_template_invite_only', wait_time=5).first.click()
        time.sleep(.2)
        roles_that_can_invite_dropdown = self.browser.find_by_css(".permissionrolefield")[0]
        self.select_from_multiselect("forwards", search_within=roles_that_can_invite_dropdown)
        self.browser.find_by_id('submit_apply_template', wait_time=5).first.click()
        time.sleep(.75)

        # check that the template has been applied
        self.browser.reload()
        self.browser.find_by_id('governance_button', wait_time=5).first.click()
        self.browser.find_by_id('group_membership_settings_button', wait_time=5).first.click()
        permissions_display = self.browser.find_by_css("#add_member_permissions * .permission-display", wait_time=5)
        permissions = [item.text for item in permissions_display]
        self.assertTrue("those with role forwards have permission to add members to community" in permissions)

    def test_rejected_template(self):

        # Crystal tries to apply the template, but she doesn't get the interface because she doesn't have permission
        self.login_user("crystaldunn", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button', wait_time=5).first.click()
        self.browser.find_by_id('group_membership_settings_button', wait_time=5).first.click()
        button = self.browser.find_by_id('membership_templates_link', wait_time=5)
        self.assertEquals(len(button), 0)

    def test_apply_template_with_condition(self):

        # set a permission and condition on permission

        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button', wait_time=5).first.click()
        self.browser.find_by_id('forwards_editrole', wait_time=5)[0].scroll_to()
        self.browser.find_by_id('forwards_editrole', wait_time=5).first.click()
        permissions = [item.text for item in self.browser.find_by_css(".permission-display", wait_time=5)]
        self.assertEquals(permissions, [])
        self.browser.find_by_id('add_permission_button', wait_time=5).first.click()
        self.select_from_multiselect("Apply template")
        self.browser.find_by_id('save_permission_button', wait_time=5).first.click()
        time.sleep(1)

        perm_element = self.browser.find_by_text("those with role forwards have permission to apply template", wait_time=5)
        cond_id = "_".join(["condition"] + perm_element[0]["id"].split("_")[1:])
        condition_element = self.browser.find_by_id(cond_id, wait_time=5).first
        condition_element.find_by_text("add condition", wait_time=5).first.click()
        self.browser.find_by_id("new_condition", wait_time=5).first.click()
        self.browser.select("condition_select", "ApprovalCondition")

        element_containing_role_dropdown = self.browser.find_by_css(".permissionrolefield", wait_time=5)[0]
        self.select_from_multiselect("forwards", search_within=element_containing_role_dropdown)
        self.browser.find_by_id('save_condition_button', wait_time=5).first.click()
        time.sleep(1)
        self.browser.back()

        # new user tries to apply a template
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button', wait_time=5).first.click()
        self.browser.find_by_id('group_membership_settings_button', wait_time=5)[0].scroll_to()
        self.browser.find_by_id('group_membership_settings_button', wait_time=5).first.click()
        self.browser.find_by_id('membership_templates_link', wait_time=5)[0].scroll_to()
        self.browser.find_by_id('membership_templates_link', wait_time=5).first.click()
        self.browser.find_by_id('select_template_invite_only', wait_time=5).first.click()
        roles_that_can_invite_dropdown = self.browser.find_by_css(".permissionrolefield", wait_time=5)[0]
        self.select_from_multiselect("forwards", search_within=roles_that_can_invite_dropdown)
        self.browser.find_by_id('submit_apply_template', wait_time=5).first.click()
        time.sleep(.2)
        self.assertTrue(self.browser.is_text_present("There is a condition"))
        self.browser.back()

        # check that the template has not been applied
        self.browser.reload()
        permissions = [item.text for item in self.browser.find_by_css("#add_member_permissions * .permission-display", wait_time=5)]
        self.assertFalse("those with role forwards have permission to add members to community" in permissions)

        # log back in as pinoe, approve
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('group_history_button', wait_time=5).first.click()
        self.browser.find_by_text("link", wait_time=5)[0].click()
        time.sleep(.25)
        self.assertTrue(self.browser.is_text_present('Please approve or reject this action.'))
        self.browser.find_by_css("#btn-radios-1 > label:nth-child(1) > span", wait_time=5).first.click()
        self.browser.find_by_id('save_approve_choice', wait_time=5).first.click()

        # check that the template has been applied
        time.sleep(.25)
        self.browser.reload()
        self.browser.back()
        self.browser.back()
        self.browser.find_by_id('governance_button', wait_time=5).first.click()
        self.browser.find_by_id('group_membership_settings_button', wait_time=5).first.click()
        permissions = [item.text for item in self.browser.find_by_css("#add_member_permissions * .permission-display", wait_time=5)]
        self.assertTrue("those with role forwards have permission to add members to community" in permissions)


class MembershipTestCase(BaseTestCase):

    def setUp(self):
        # Basic setup
        self.create_users()
        self.create_templates()
        self.actor = User.objects.first()
        self.client = Client(actor=self.actor)
        self.community = self.client.Community.create_community(name="USWNT")
        self.client.update_target_on_all(target=self.community)
        self.client.Community.add_members(member_pk_list=[user.pk for user in User.objects.all()[:4]])
        self.client.Community.add_role(role_name="forwards")
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
        self.browser.find_by_id('governance_button', wait_time=5).first.click()
        self.browser.find_by_id('members_member_count', wait_time=5)[0].scroll_to()
        self.assertEquals(self.browser.find_by_id('members_member_count', wait_time=5)[0].text, "4 people")

        # apply anyone can join template
        self.browser.find_by_id('group_membership_settings_button', wait_time=5).first.click()
        self.browser.find_by_id('membership_templates_link', wait_time=5).first.click()
        self.browser.find_by_id('select_template_anyone_can_join', wait_time=5).first.click()
        self.browser.find_by_id('submit_apply_template', wait_time=5).first.click()

        # check template was applied
        permission_display = self.browser.find_by_css("#add_member_permissions * .permission-display", wait_time=5)
        self.assertEquals([item.text for item in permission_display],
            ["anyone has permission to add members to community, but a user can only add themselves"])

        # random person can join
        self.login_user("midgepurce", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button', wait_time=5).first.click()
        self.browser.find_by_id("join_group_button", wait_time=5).first.click()
        time.sleep(.5)  # needs a moment to query backend and update

        # we should now have 5 members, not 4
        self.browser.find_by_id('members_member_count', wait_time=5)[0].scroll_to()
        self.assertEquals(self.browser.find_by_id('members_member_count', wait_time=5)[0].text, "5 people")

    def test_invite_only(self):

        # we start with 4 members
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button').first.click()
        self.browser.find_by_id('members_member_count')[0].scroll_to()
        self.assertEquals(self.browser.find_by_id('members_member_count')[0].text, "4 people")

        # apply the template
        self.browser.find_by_id('group_membership_settings_button').first.click()
        time.sleep(.2)
        self.browser.find_by_id('membership_templates_link').first.click()
        self.browser.find_by_id('select_template_invite_only').first.click()
        roles_that_can_invite_dropdown = self.browser.find_by_css(".permissionrolefield")[0]
        self.select_from_multiselect("forwards", search_within=roles_that_can_invite_dropdown)
        self.browser.find_by_id('submit_apply_template', wait_time=5).first.click()

        # check that the template has been applied
        permissions = [item.text for item in self.browser.find_by_css("#add_member_permissions * .permission-display", wait_time=5)]
        self.assertEquals(permissions, ["those with role forwards have permission to add members to community"])

        # Midge can't join
        self.login_user("midgepurce", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button', wait_time=5).first.click()
        self.assertEquals(len(self.browser.find_by_id("join_group_button", wait_time=5)), 0)

        # but Christen, a forward, can invite her
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button', wait_time=5).first.click()
        self.browser.find_by_id('group_membership_display_button', wait_time=5).first.click()
        self.browser.find_by_id('add_member_button', wait_time=5).first.click()
        time.sleep(.25)
        self.select_from_multiselect(selection="midgepurce")
        time.sleep(.5)
        self.assertEquals(["midgepurce"], self.get_selected_in_multiselect())
        self.browser.find_by_id('save_add_member_button', wait_time=5).first.click()
        time.sleep(.25)
        self.assertTrue(self.browser.is_text_present(
            "There is a condition on your action which must be resolved before your action can be implemented.", wait_time=5))

        # Christen doesn't have permission to approve the invite
        self.browser.back()
        self.browser.find_by_id('group_history_button', wait_time=5).first.click()
        self.browser.find_by_text("link", wait_time=5).first.click()
        time.sleep(.25)
        self.assertTrue(self.browser.is_text_present('You do not have permission to approve or reject this action.'))

        # Midge approves, and now there are 5 members
        self.login_user("midgepurce", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('group_history_button', wait_time=5).first.click()
        self.browser.find_by_text("link", wait_time=5).first.click()
        self.assertTrue(self.browser.is_text_present('Please approve or reject this action.', wait_time=5))
        self.browser.find_by_css("#btn-radios-1 > label:nth-child(1) > span", wait_time=5).first.click()
        self.browser.find_by_id('save_approve_choice', wait_time=5).first.click()
        time.sleep(.25)
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button', wait_time=5).first.click()
        self.browser.find_by_id('members_member_count', wait_time=5)[0].scroll_to()
        self.assertEquals(self.browser.find_by_id('members_member_count', wait_time=5).text, "5 people")

    def test_anyone_can_request_to_join(self):

        # we start with 4 members
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button', wait_time=5).first.click()
        self.browser.find_by_id('members_member_count', wait_time=5)[0].scroll_to()
        self.assertEquals(self.browser.find_by_id('members_member_count', wait_time=5)[0].text, "4 people")

        # apply anyone can join template
        self.browser.find_by_id('group_membership_settings_button', wait_time=5).first.click()
        self.browser.find_by_id('membership_templates_link', wait_time=5).first.click()
        self.browser.find_by_id('select_template_anyone_can_request_to_join', wait_time=5).first.click()
        roles_that_can_approve_dropdown = self.browser.find_by_css(".permissionrolefield", wait_time=5)[0]
        self.select_from_multiselect("forwards", search_within=roles_that_can_approve_dropdown)
        self.browser.find_by_id('submit_apply_template', wait_time=5).first.click()

        # check template was applied
        permissions = [item.text for item in self.browser.find_by_css("#add_member_permissions * .permission-display", wait_time=5)]
        self.assertEquals(permissions, ["anyone has permission to add members to community, but a user can only add themselves"])
        condition = self.browser.find_by_text("on the condition that those with role forwards needs to approve this action")
        self.assertEquals(len(condition), 1)

        # random person can request but they are not added yet
        self.login_user("midgepurce", "badlands2020")
        self.go_to_group("USWNT")
        time.sleep(1)
        self.browser.find_by_id('governance_button', wait_time=5).first.click()
        time.sleep(1)
        self.browser.find_by_id("join_group_button", wait_time=5).first.click()
        time.sleep(1) # may be necessary for scroll_tos?
        self.browser.find_by_id('members_member_count')[0].scroll_to()
        self.assertEquals(self.browser.find_by_id('members_member_count', wait_time=5)[0].text, "4 people")

        # Christen Press, with role forwards, approves
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('group_history_button', wait_time=5).first.click()
        self.browser.find_by_text("link", wait_time=5).first.click()
        self.assertTrue(self.browser.is_text_present('Please approve or reject this action.', wait_time=5))
        self.browser.find_by_css("#btn-radios-1 > label:nth-child(1) > span", wait_time=5).first.click()
        self.browser.find_by_id('save_approve_choice', wait_time=5).first.click()
        text = "You have approved midgepurce's action. Nothing further is needed from you."
        self.assertTrue(self.browser.is_text_present(text, wait_time=5))

        # we should now have 5 members, not 4
        self.browser.reload()
        self.browser.back()
        self.browser.back()
        self.browser.find_by_id('governance_button', wait_time=5).first.click()
        self.browser.find_by_id('members_member_count', wait_time=5)[0].scroll_to()
        self.assertEquals(self.browser.find_by_id('members_member_count', wait_time=5)[0].text, "5 people")

    # TODO: suite of comments test cases


class ListTestCase(BaseTestCase):

    def setUp(self):

        # Basic setup
        self.create_users()
        self.create_templates()
        self.actor = User.objects.first()
        self.client = Client(actor=self.actor)
        self.community = self.client.Community.create_community(name="USWNT")
        self.client.update_target_on_all(target=self.community)
        self.client.Community.add_members(member_pk_list=[user.pk for user in User.objects.all()[:4]])
        self.client.Community.add_role(role_name="forwards")
        pinoe = User.objects.get(username="meganrapinoe")
        press = User.objects.get(username="christenpress")
        self.client.Community.add_people_to_role(role_name="forwards", people_to_add=[pinoe.pk, press.pk])

    def test_list_functionality_for_governor(self):

        # create a list
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('new_list_button').first.click()
        self.browser.fill('list_name', "Best NWSL Teams")
        self.browser.fill('list_description', "The best NWSL teams, in order of awesomeness")
        self.browser.find_by_id('add_list_button').first.click()
        self.browser.back()
        self.assertTrue(self.browser.is_text_present('The best NWSL teams, in order of awesomeness'))

        # go to list & edit it
        self.browser.find_by_id('link_to_list_0').first.click()
        self.browser.find_by_id('edit_list_button').first.click()
        self.browser.fill('list_name', "Best NWSL Teams!")
        self.browser.fill('list_description', "The best NWSL teams, in order of awesomeness!")
        self.browser.find_by_id('edit_list_save_button').first.click()
        self.browser.back()
        self.assertTrue(self.browser.is_text_present('The best NWSL teams, in order of awesomeness!'))

        # add some items
        self.browser.find_by_id('add_row_button').first.click()
        self.browser.fill('content', 'Chicago Red Stars')
        self.browser.find_by_id('add_row_save_button').first.click()
        self.assertTrue(self.browser.is_text_present('Chicago Red Stars'))
        self.browser.find_by_id('add_row_button').first.click()
        self.browser.fill('content', 'NJ Sky Blue')
        self.browser.find_by_id('index')[0].type(Keys.RIGHT)
        self.browser.find_by_id('add_row_save_button').first.click()
        self.browser.find_by_id('add_row_button').first.click()
        self.browser.fill('content', 'Washington Spirit')
        self.browser.find_by_id('add_row_save_button').first.click()
        time.sleep(.5)
        teams = [team.text for team in self.browser.find_by_xpath("//td")]
        teams = list(filter(lambda x: x not in ["edit\ndelete\nmove", "0", "1", "2", "3"], teams))
        self.assertEquals(teams, ["Washington Spirit", "Chicago Red Stars", "NJ Sky Blue"])

        # edit a row
        self.browser.find_by_id('edit_row_2').first.click()
        self.browser.fill('content', 'Sky Blue FC')
        self.browser.find_by_id('edit_row_save_button').first.click()
        teams = [team.text for team in self.browser.find_by_xpath("//td")]
        teams = list(filter(lambda x: x not in ["edit\ndelete\nmove", "0", "1", "2", "3"], teams))
        self.assertEquals(teams, ["Washington Spirit", "Chicago Red Stars", "Sky Blue FC"])

        # delete a row
        self.browser.find_by_id('delete_row_2').first.click()
        time.sleep(.5)
        teams = [team.text for team in self.browser.find_by_xpath("//td")]
        teams = list(filter(lambda x: x not in ["edit\ndelete\nmove", "0", "1", "2", "3"], teams))
        self.assertEquals(teams, ["Washington Spirit", "Chicago Red Stars"])

        # delete list
        self.browser.find_by_id('delete_list_button').first.click()
        self.assertTrue(self.browser.is_text_present('You do not have any lists yet.'))

    def test_list_check_permissions(self):

        # setup
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('new_list_button').first.click()
        self.browser.fill('list_name', "Best NWSL Teams")
        self.browser.fill('list_description', "The best NWSL teams, in order of awesomeness")
        self.browser.find_by_id('add_list_button').first.click()
        self.browser.back()
        self.browser.find_by_id('link_to_list_0').first.click()
        self.browser.find_by_id('add_row_button').first.click()
        self.browser.fill('content', 'Washington Spirit')
        self.browser.find_by_id('add_row_save_button').first.click()

        self.assertEquals(len(self.browser.find_by_id('edit_list_button')), 1)
        self.assertEquals(len(self.browser.find_by_id('delete_list_button')), 1)
        self.assertEquals(len(self.browser.find_by_id('add_row_button')), 1)
        self.assertEquals(len(self.browser.find_by_id('edit_row_0')), 1)
        self.assertEquals(len(self.browser.find_by_id('delete_row_0')), 1)

        # new user has no permissions, can't do most things
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('link_to_list_0').first.click()

        self.assertEquals(len(self.browser.find_by_id('edit_list_button')), 0)
        self.assertEquals(len(self.browser.find_by_id('delete_list_button')), 0)
        self.assertEquals(len(self.browser.find_by_id('add_row_button')), 0)
        self.assertEquals(len(self.browser.find_by_id('edit_row_0')), 0)
        self.assertEquals(len(self.browser.find_by_id('delete_row_0')), 0)

    def test_enhanced_list_configuration(self):

        # rapinoe begins creating a list
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('new_list_button').first.click()
        self.browser.fill('list_name', "Best NWSL Teams")
        self.browser.fill('list_description', "The best NWSL teams, in our honest opinion")

        # can't delete default column until new one is added
        self.browser.find_by_id('delete_column_content').first.click()
        self.assertTrue(self.browser.is_text_present('Must have at least one column'))
        self.browser.find_by_css(".alert > button")[0].click()

        # add a column, now can delete the old one
        self.browser.fill('column_name', "Team Name")
        self.browser.find_by_id('column_required').check()
        self.browser.find_by_id('add_new_col_button').first.click()
        self.browser.find_by_id('delete_column_content').first.click()

        # can't add a column with an empty name
        self.browser.fill('column_name', "")
        self.browser.find_by_id('add_new_col_button').first.click()
        self.assertTrue(self.browser.is_text_present('New column must have a name'))
        self.browser.find_by_css(".alert > button")[0].click()

        # can't add a column with a duplicate name
        self.browser.fill('column_name', "Team Name")
        self.browser.find_by_id('add_new_col_button').first.click()
        self.assertTrue(self.browser.is_text_present('Columns must have unique names'))
        self.browser.find_by_css(".alert > button")[0].click()

        # can add a new unique column
        self.browser.find_by_id('column_required').uncheck()
        self.browser.fill('column_name', "City")
        self.browser.find_by_id('add_new_col_button').first.click()
        self.browser.fill('column_name', "State")
        self.browser.find_by_id('add_new_col_button').first.click()

        # save successfully
        self.browser.find_by_id('add_list_button').first.click()
        self.browser.back()
        self.browser.find_by_id('link_to_list_0').first.click()

        # rapinoe adds two rows with original configuration
        self.browser.find_by_id('add_row_button').first.click()
        self.browser.fill('Team Name', 'Sky Blue')
        self.browser.fill('State', 'NJ')
        self.browser.find_by_id('add_row_save_button').first.click()
        self.browser.find_by_id('add_row_button').first.click()
        self.browser.fill('Team Name', 'Spirit')
        self.browser.fill('City', 'Washington')
        self.browser.fill('State', 'DC')
        self.browser.find_by_id('add_row_save_button').first.click()

        # rapinoe edits configuration but can't add a required field without default
        self.browser.find_by_id('edit_list_button').first.click()
        time.sleep(.25)
        self.browser.find_by_id('column_required').check()
        self.browser.fill('column_name', "Is Reigning Champion")
        self.browser.find_by_id('add_new_col_button').first.click()
        self.assertTrue(self.browser.is_text_present('If column is required, must supply default value'))

        # with default supplied, she adds a new field
        self.browser.fill('column_default', "No")
        self.browser.find_by_id('add_new_col_button').first.click()
        self.browser.find_by_id('edit_list_save_button').first.click()

        # upated list missing removed field, has new field
        time.sleep(.5)
        teams = [team.text for team in self.browser.find_by_xpath("//td")]
        teams = list(filter(lambda x: x not in ["edit\ndelete\nmove", "0", "1", "2", "3"], teams))
        self.assertEquals(teams, ['Spirit', 'Washington', 'DC', 'No', 'Sky Blue', '', 'NJ', 'No'])

        # new add row has different prompts
        self.browser.find_by_id('add_row_button').first.click()
        self.assertTrue(self.browser.is_text_present("Team Name"))
        self.assertTrue(self.browser.is_text_present("City"))
        self.assertTrue(self.browser.is_text_present("State"))
        self.assertTrue(self.browser.is_text_present("Is Reigning Champion"))
        self.assertTrue(self.browser.is_text_present('The default value for this column is No.'))


class DependentFieldTestCase(BaseTestCase):

    def setUp(self):

        # Basic setup
        self.create_users()
        self.create_templates()
        self.actor = User.objects.first()
        self.client = Client(actor=self.actor)
        self.community = self.client.Community.create_community(name="USWNT")
        self.client.update_target_on_all(target=self.community)
        self.client.Community.add_members(member_pk_list=[user.pk for user in User.objects.all()[:4]])
        self.client.Community.add_role(role_name="forwards")
        pinoe = User.objects.get(username="meganrapinoe")
        press = User.objects.get(username="christenpress")
        self.client.Community.add_people_to_role(role_name="forwards", people_to_add=[pinoe.pk, press.pk])

        # delete default membership permission
        from concord.permission_resources.models import PermissionsItem
        for permission in PermissionsItem.objects.all():
            if permission.change_type == Changes().Communities.AddMembers:
                permission.delete()

    def test_dependent_field_created_by_posters_control_posts_template_works(self):

        # Delete existing comment permission on Forum
        from concord.permission_resources.models import PermissionsItem
        for permission in PermissionsItem.objects.all():
            if permission.change_type == Changes().Resources.AddComment:
                permission.delete()

        # Creator applies "posters control posts" template to Governance Forum
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_css(".forum-description", wait_time=5).first.click()
        time.sleep(1) # for some bizarre reason, without this sleep splinter confuses permissions button for history button
        self.browser.find_by_id("forum_permissions_button", wait_time=5).first.click()
        self.browser.find_by_id("apply_templates", wait_time=5).first.click()
        self.browser.find_by_id("select_template_posters_control_posts", wait_time=5).first.click()
        self.browser.find_by_id("submit_apply_template", wait_time=5).first.click()
        self.browser.find_by_css(".permission-display", wait_time=5)
        permissions = [item.text for item in self.browser.find_by_css(".permission-display")]
        self.assertEquals(len(permissions), 9)
        self.assertTrue(self.browser.is_text_present(
            "anyone has permission to edit comment, but only if the user is the commenter"))

        # Inspecting what was created, everything looks fine
        self.browser.find_by_css(".edit-condition.edit_comment", wait_time=5).first.click()
        self.browser.find_by_css(".edit-condition-button", wait_time=5).first.click()
        self.assertTrue(self.browser.is_text_present("set as: post's author"))
        self.browser.find_by_css(".edit-dependent-field", wait_time=5).first.click()
        self.assertTrue(self.browser.is_text_present("Choose object to depend on:"))
        self.assertEquals(self.browser.find_by_id("model_options").first.value, "actiongroupcommentpost")
        self.assertEquals(len(self.browser.find_by_id("depend_on_model_post")), 1)
        self.assertTrue(self.browser.find_by_id("depend_on_model_post").first.has_class('btn-info'))
        field_select = self.browser.find_by_css(".dependent-field-select").first
        self.assertEquals(field_select.value, "author")

        # User makes a post
        self.browser.back()
        self.browser.back()
        self.browser.find_by_id('add_post_button', wait_time=5).first.click()
        time.sleep(3)  # this seems to be the important sleep
        self.browser.fill('post_title', 'I have an idea')
        time.sleep(.5)
        self.browser.fill('post_content', "It's a good one")
        time.sleep(.5)
        self.browser.find_by_id('add_post_save_button', wait_time=5).first.click()
        time.sleep(1)
        self.assertTrue(self.browser.is_text_present('I have an idea', wait_time=5))
        # FIXME: This only breaks on headless, not sure what's going on but added lots of sleeps

        # Another user makes a comment on the post
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_css(".forum-description").first.click()
        self.browser.find_by_css(".post-content").first.click()
        self.browser.find_by_css(".add-comment").first.click()
        self.browser.fill('comment_text', "it's ok I guess")
        self.browser.find_by_id('submit_comment_button', wait_time=5).first.click()
        self.assertFalse(self.browser.is_text_present("it's ok I guess", wait_time=5))

        # User approves it
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_css(".forum-description", wait_time=5).first.click()
        self.browser.find_by_css(".post-content", wait_time=5).first.click()
        time.sleep(1) # again, without this sleep splinter confuses forum button for history button
        self.browser.find_by_id("post_history_button", wait_time=5).first.click()
        self.browser.find_by_css(".action-link-button", wait_time=5)[0].click()
        self.assertTrue(self.browser.is_text_present('Please approve or reject this action.', wait_time=5))
        self.browser.find_by_css("#btn-radios-1 > label:nth-child(1) > span", wait_time=5).first.click()
        self.browser.find_by_id('save_approve_choice', wait_time=5).first.click()
        time.sleep(.5)
        self.browser.back()
        self.browser.back()
        self.assertTrue(self.browser.is_text_present("it's ok I guess", wait_time=5))

    def test_make_dependent_field_from_scratch(self):

        # user adds a membership permission where members can add people
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button', wait_time=5).first.click()
        self.browser.find_by_id('group_membership_settings_button', wait_time=5).first.click()
        self.browser.find_by_id('add_permission_button', wait_time=5).first.click()
        self.select_from_multiselect("members")
        self.browser.find_by_id('save_permission_button', wait_time=5).first.click()

        # adds an approval condition with permission_actors dependency field as member_pk_list
        self.browser.find_by_css('.add-condition', wait_time=5).first.click()
        self.browser.find_by_id("new_condition", wait_time=5).first.click()
        self.browser.select("condition_select", "ApprovalCondition")
        self.browser.find_by_css('.add-dependent-field', wait_time=5)[1].click()
        self.browser.find_by_id('depend_on_model_action', wait_time=5).first.click()
        self.browser.select('dependent-field-select', 'member_pk_list')
        self.browser.find_by_id('save-dependent-field', wait_time=5).first.click()
        self.browser.find_by_id('save_condition_button', wait_time=5).first.click()

        # sets approve permission via dependency field as member_pk_list
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button', wait_time=5)[0].click()
        self.browser.find_by_id('group_membership_display_button', wait_time=5).first.click()
        self.browser.find_by_id('add_member_button', wait_time=5).first.click()
        self.select_from_multiselect(selection="midgepurce")
        self.browser.find_by_id('save_add_member_button', wait_time=5).first.click()
        text_to_match = 'There is a condition on your action which must be resolved before your action can be implemented.'
        self.assertTrue(self.browser.is_text_present(text_to_match, wait_time=5))

        # Christen doesn't have permission to approve the invite
        self.browser.back()
        self.browser.find_by_id('group_history_button', wait_time=5).first.click()
        self.browser.find_by_text("link", wait_time=5).first.click()
        text_to_match = 'You do not have permission to approve or reject this action.'
        self.assertTrue(self.browser.is_text_present(text_to_match, wait_time=5))

        # Midge approves, and now there are 5 members
        self.login_user("midgepurce", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('group_history_button', wait_time=5).first.click()
        self.browser.find_by_text("link", wait_time=5).first.click()
        self.assertTrue(self.browser.is_text_present('Please approve or reject this action.'))
        self.browser.find_by_css("#btn-radios-1 > label:nth-child(1) > span", wait_time=5).first.click()
        self.browser.find_by_id('save_approve_choice', wait_time=5).first.click()
        time.sleep(.25)
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button', wait_time=5).first.click()
        self.browser.find_by_id('members_member_count', wait_time=5)[0].scroll_to()
        self.assertEquals(self.browser.find_by_id('members_member_count', wait_time=5).text, "5 people")


class MultipleConditionsTestCase(BaseTestCase):

    def setUp(self):

        # Basic setup
        self.create_users()
        self.create_templates()
        self.actor = User.objects.first()
        self.client = Client(actor=self.actor)
        self.community = self.client.Community.create_community(name="USWNT")
        self.client.update_target_on_all(target=self.community)
        self.client.Community.add_members(member_pk_list=[user.pk for user in User.objects.all()[:4]])
        self.client.Community.add_role(role_name="forwards")
        pinoe = User.objects.get(username="meganrapinoe")
        press = User.objects.get(username="christenpress")
        heath = User.objects.get(username="tobinheath")
        self.client.Community.add_people_to_role(role_name="forwards", people_to_add=[pinoe.pk, press.pk, heath.pk])

        # Permission setup
        action, self.permission = self.client.PermissionResource.add_permission(
            permission_type=Changes().Communities.AddRole, permission_roles=["forwards"])

    def test_multiple_conditions(self):

        # add a condition
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button', wait_time=5)[0].click()
        self.browser.find_by_id('forwards_editrole', wait_time=5)[0].scroll_to()
        self.browser.find_by_id('forwards_editrole', wait_time=5).first.click()
        perm_element = self.browser.find_by_text(
            "those with role forwards have permission to add role to community", wait_time=5)
        cond_id = "_".join(["condition"] + perm_element[0]["id"].split("_")[1:])
        condition_element = self.browser.find_by_id(cond_id, wait_time=5).first
        condition_element.find_by_text("add condition", wait_time=5).first.click()
        self.browser.find_by_id("new_condition", wait_time=5).first.click()
        self.browser.select("condition_select", "ApprovalCondition")
        element_containing_role_dropdown = self.browser.find_by_css(".permissionactorfield", wait_time=5)[0]
        self.select_from_multiselect("christenpress", search_within=element_containing_role_dropdown)
        self.browser.find_by_id('save_condition_button', wait_time=5).first.click()

        # add another condition
        self.browser.find_by_id("new_condition", wait_time=5).first.click()
        self.browser.select("condition_select", "ApprovalCondition")
        element_containing_role_dropdown = self.browser.find_by_css(".permissionactorfield")[0]
        self.select_from_multiselect("tobinheath", search_within=element_containing_role_dropdown)
        self.browser.find_by_id('save_condition_button', wait_time=5).first.click()

        # add a third condition
        self.browser.find_by_id("new_condition", wait_time=5).first.click()
        self.browser.select("condition_select", "ApprovalCondition")
        element_containing_role_dropdown = self.browser.find_by_css(".permissionactorfield", wait_time=5)[0]
        self.select_from_multiselect("crystaldunn", search_within=element_containing_role_dropdown)
        self.browser.find_by_id('save_condition_button', wait_time=5).first.click()

        time.sleep(.5)

        # delete third condition
        self.browser.find_by_css(".edit-condition-button", wait_time=5).last.click()
        self.browser.find_by_id("delete_condition_button", wait_time=5).first.click()

        time.sleep(.5)

        # edit one of the two remaining conditions
        self.browser.find_by_css(".edit-condition-button", wait_time=5).first.click()
        element_containing_role_dropdown = self.browser.find_by_css(".permissionactorfield", wait_time=5)[0]
        self.select_from_multiselect("tobinheath", search_within=element_containing_role_dropdown)
        self.browser.find_by_id("save_edit_condition_button", wait_time=5).first.click()

        time.sleep(.5)

        # take action to trigger the new conditions
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button', wait_time=5)[0].click()
        self.browser.find_by_id('add_role_button', wait_time=5).first.click()
        self.browser.fill('role_name', 'midfielders')
        self.browser.find_by_id('save_role_button', wait_time=5).first.click()
        self.assertTrue(self.browser.is_text_present(
            'There is a condition on your action which must be resolved before your action can be implemented.',
            wait_time=5))

        # resolve each of the two remaining conditions
        self.login_user("tobinheath", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('group_history_button', wait_time=5)[0].click()
        self.browser.find_by_css(".action-link-button", wait_time=5)[0].click()
        self.assertTrue(self.browser.is_text_present('Please approve or reject this action.', wait_time=5))
        self.browser.find_by_css("#btn-radios-1 > label:nth-child(1) > span", wait_time=5).first.click()
        time.sleep(.25)
        self.browser.find_by_id('save_approve_choice', wait_time=5).first.click()
        time.sleep(.25)
        text = "You have approved christenpress's action. Nothing further is needed from you."
        self.assertTrue(self.browser.is_text_present(text, wait_time=5))
        self.browser.find_by_css('.card-header-tabs li a', wait_time=5).last.click()
        self.assertTrue(self.browser.is_text_present('Please approve or reject this action.', wait_time=5))
        self.browser.find_by_css("#btn-radios-1 > label:nth-child(1) > span", wait_time=5).first.click()
        time.sleep(.25)
        self.browser.find_by_id('save_approve_choice', wait_time=5).first.click()
        time.sleep(.25)
        text = "You have approved christenpress's action. Nothing further is needed from you."
        self.assertTrue(self.browser.is_text_present(text, wait_time=5))
        time.sleep(.5)

        # action implemented
        self.browser.reload()
        self.browser.find_by_id('governance_button', wait_time=5)[0].click()
        roles = [item.text for item in self.browser.find_by_css(".role_name_display", wait_time=5)]
        self.assertEquals(roles, ["members", "forwards", "midfielders"])



