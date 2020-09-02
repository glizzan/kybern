import time, os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from splinter import Browser
from django.conf import settings
from selenium import webdriver

from django.contrib.auth.models import User
from concord.actions.utils import Changes, Client
from groups.models import Forum


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
        self.actor = User.objects.first()
        self.client = Client(actor=self.actor)
        self.community = self.client.Community.create_community(name="USWNT")

    def test_create_group(self):
        self.login_user("meganrapinoe", "badlands2020")
        self.browser.visit(self.live_server_url + "/groups/list/")
        self.browser.links.find_by_text('Create a group').first.click()
        self.browser.fill('name', 'NWSL')
        self.browser.fill('group_description', 'For NWSL players')
        self.browser.find_by_id('create_group_button').first.click()
        self.assertTrue(self.browser.is_text_present('edit group'))  # shows we're on group detail page now
        self.assertTrue(self.browser.is_text_present("NWSL's Forums"))  # shows we're on newly created detail page now

    def test_add_members_to_group(self):
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button')[0].click()
        self.browser.find_by_id('members_member_count')[0].scroll_to()
        self.assertEquals(self.browser.find_by_id('members_member_count')[0].text, "1 people")
        self.browser.find_by_id('group_membership_display_button').first.click()
        time.sleep(.25)
        names = [item.text for item in self.browser.find_by_css("span#current_member_list>span.badge")]
        self.assertEquals(names, ["meganrapinoe"])
        self.browser.find_by_id('add_member_button').first.click()
        time.sleep(.25)
        self.select_from_multiselect(selection="christenpress")
        time.sleep(.5)
        self.assertEquals(["christenpress"], self.get_selected_in_multiselect())
        self.browser.find_by_id('save_add_member_button').first.click()
        time.sleep(.5)
        names = [item.text for item in self.browser.find_by_css("span#current_member_list>span.badge")]
        self.assertEquals(names, ["meganrapinoe", "christenpress"])
        self.browser.find_by_css(".close").first.click()  # close modal
        self.assertEquals(self.browser.find_by_id('members_member_count').text, "2 people")

    def test_create_role(self):
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button')[0].click()
        self.browser.find_by_id('add_role_button')[0].scroll_to()
        self.browser.find_by_id('add_role_button').first.click()
        self.browser.fill('role_name', 'forwards')
        self.browser.find_by_id('save_role_button').first.click()
        self.browser.find_by_css(".close").first.click()  # close modal
        time.sleep(.5)
        roles = [item.text for item in self.browser.find_by_css(".role_name_display")]
        self.assertEquals(roles, ["members", "forwards"])

    def test_add_members_to_role(self):
        self.test_add_members_to_group()
        self.test_create_role()
        self.assertEquals(self.browser.find_by_id('forwards_member_count').text, "0 people")
        self.browser.find_by_id('forwards_changemembers').first.click()
        self.select_from_multiselect(selection="christenpress")
        time.sleep(.5)
        self.assertEquals(["christenpress"], self.get_selected_in_multiselect())
        self.browser.find_by_id('save_member_changes').first.click()
        self.browser.find_by_css(".close").first.click()  # close modal
        time.sleep(.5)
        self.assertEquals(self.browser.find_by_id('forwards_member_count').text, "1 people")


class PermissionsTestCase(BaseTestCase):

    def setUp(self):
        self.create_users()
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
        self.browser.select("permission_select",
                            "concord.communities.state_changes.RemoveMembersStateChange")
        self.browser.find_by_id('save_permission_button').first.click()
        time.sleep(.5)
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
        self.assertEquals(self.browser.find_by_id('members_member_count').text, "8 people")
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
        self.assertEquals(self.browser.find_by_id('members_member_count').text, "7 people")

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
        self.assertTrue(self.browser.is_text_present('meganrapinoe added role forwards to USWNT'))


class ActionConditionsTestCase(BaseTestCase):

    def setUp(self):

        # Basic setup
        self.create_users()
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
        self.browser.find_by_id('governance_button')[0].click()
        self.browser.find_by_id('forwards_editrole')[0].scroll_to()
        self.browser.find_by_id('forwards_editrole').first.click()
        time.sleep(.25)
        perm_element = self.browser.find_by_text("those with role forwards have permission to add role to community")
        cond_id = "_".join(["condition"] + perm_element[0]["id"].split("_")[1:])
        self.browser.find_by_id(cond_id).first.click()
        self.browser.select("condition_select", "VoteCondition")
        element_containing_role_dropdown = self.browser.find_by_css(".permissionrolefield")[0]
        self.select_from_multiselect("forwards", search_within=element_containing_role_dropdown)
        self.browser.find_by_id('save_condition_button').first.click()
        time.sleep(.25)
        self.browser.find_by_css(".close").first.click()  # close modal

        # Someone with the permission tries to take action (use asserts to check for condition error text)
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button')[0].click()
        self.browser.find_by_id('add_role_button').first.click()
        self.browser.fill('role_name', 'midfielders')
        self.browser.find_by_id('save_role_button').first.click()
        time.sleep(.25)
        self.assertTrue(self.browser.is_text_present('There is a condition on your action which must be resolved before your action can be implemented.'))
        
        # Click through to condition
        self.browser.find_by_id('condition_link')[0].click()
        self.assertTrue(self.browser.is_text_present('Please cast your vote'))
        

class ApprovalConditionsTestCase(BaseTestCase):

    def setUp(self):

        # create group, add members, add roles, add members to role
        self.create_users()
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
        self.client.PermissionResource.set_target(self.permission)
        self.client.PermissionResource.add_condition_to_permission(
            condition_type="approvalcondition", permission_data=perm_data)

        # have person take action that triggers permission/condition
        self.client.Community.set_actor(heath)
        self.client.Community.add_role(role_name="midfielders")

    def test_approve_implements_action(self):

        # User navigates to action history and approves action
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('group_history_button')[0].click()
        self.assertTrue(self.browser.is_text_present('tobinheath asked to add role midfielders to USWNT')) 
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
        css_str = "#action_history_table_element > tbody > tr:nth-child(1) > td:nth-child(4)"
        self.assertTrue(self.browser.find_by_css(css_str)[0].text, "implemented")

    def test_reject_rejects_action(self):

        # User navigates to action history and approves action
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('group_history_button')[0].click()
        self.assertTrue(self.browser.is_text_present('tobinheath asked to add role midfielders to USWNT')) 
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
        css_str = "#action_history_table_element > tbody > tr:nth-child(1) > td:nth-child(4)"
        self.assertTrue(self.browser.find_by_css(css_str)[0].text, "rejected")

    def test_person_without_permission_to_approve_cant_approve(self):
        self.login_user("emilysonnett", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('group_history_button')[0].click()
        self.assertTrue(self.browser.is_text_present('tobinheath asked to add role midfielders to USWNT')) 
        self.browser.find_by_css(".action-link-button")[0].click()
        self.assertTrue(self.browser.is_text_present('You do not have permission to approve or reject this action.'))


class VotingConditionTestCase(BaseTestCase):

    def setUp(self):

        # create group, add members, add roles, add members to role
        self.create_users()
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
        self.client.PermissionResource.set_target(self.permission)
        self.client.PermissionResource.add_condition_to_permission(
            condition_type="votecondition", permission_data=perm_data)

        # have person take action that triggers permission/condition
        self.client.Community.set_actor(heath)
        self.client.Community.add_role(role_name="midfielders")

    def test_yea_updates_vote_results(self):

        # User navigates to action history and votes yea
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('group_history_button')[0].click()
        self.assertTrue(self.browser.is_text_present('tobinheath asked to add role midfielders to USWNT')) 
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
        self.assertTrue(self.browser.is_text_present('tobinheath asked to add role midfielders to USWNT')) 
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
        self.assertTrue(self.browser.is_text_present('tobinheath asked to add role midfielders to USWNT')) 
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
        self.assertTrue(self.browser.is_text_present('tobinheath asked to add role midfielders to USWNT')) 
        self.browser.find_by_css(".action-link-button")[0].click()
        self.assertTrue(self.browser.is_text_present('You are not eligible to vote.'))


class ForumsTestCase(BaseTestCase):

    def setUp(self):

        self.create_users()
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
        self.browser.find_by_css(".forum-description").first.click()
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
        self.browser.find_by_css(".close").first.click()  # close modal

        # delete forum
        self.browser.find_by_css(".forum-description").first.click()
        self.browser.find_by_id('delete_forum_button').first.click()
        time.sleep(.25)
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
        self.browser.fill('post_title', 'I have a great idea')
        self.browser.find_by_id('edit_post_save_button').first.click()
        self.assertTrue(self.browser.is_text_present('I have a great idea'))

        # Delete post
        self.browser.find_by_id('delete_post_button').first.click()
        time.sleep(.25)
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

        # Add permissions
        self.browser.find_by_id("forum_permissions").first.click()
        permissions = [item.text for item in self.browser.find_by_css(".permission-display")]
        self.assertEquals(permissions, [])
        self.browser.find_by_id('add_permission_button').first.click()
        self.browser.select("permission_select", "groups.state_changes.EditForumStateChange")
        time.sleep(.25)
        element_containing_role_dropdown = self.browser.find_by_css(".permissionrolefield")[0]
        self.select_from_multiselect("forwards", search_within=element_containing_role_dropdown)
        self.browser.find_by_id('save_permission_button').first.click()
        time.sleep(.25)
        permissions = [item.text for item in self.browser.find_by_css(".permission-display")]
        self.assertEquals(permissions, ["those with role forwards have permission to edit a forum"])

    # def test_add_condition_to_permission_on_forum(self):
    #     pass

    # def test_add_condition_to_permission_on_forum_actually_works(self):
    #     basically do the previous test, then go look at the history for the forum
    #     pass


class TemplatesTestCase(BaseTestCase):

    def setUp(self):
        # create group, add members, add roles, add members to role
        self.create_users()
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

        # generate templates
        from concord.actions.template_library import create_all_templates
        create_all_templates()

    def test_apply_template_with_no_conditions(self):

        # apply the template
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button').first.click()
        self.browser.find_by_id('group_membership_settings_button').first.click()
        time.sleep(.2)
        self.browser.find_by_id('browse_membership_templates_button').first.click()
        self.browser.find_by_id('apply_template_invite_only').first.click()
        roles_that_can_invite_dropdown = self.browser.find_by_css(".permissionrolefield")[0]
        self.select_from_multiselect("forwards", search_within=roles_that_can_invite_dropdown)
        self.browser.find_by_id('submit_apply_template').first.click()

        # check that the template has been applied
        self.browser.reload()
        self.browser.find_by_id('governance_button').first.click()
        self.browser.find_by_id('group_membership_settings_button').first.click()
        time.sleep(.2)
        permissions = [item.text for item in self.browser.find_by_css("#add_member_permissions * .permission-display")]
        self.assertEquals(permissions, ["those with role forwards have permission to add members to community"])

    def test_rejected_template(self):

        # Crystal tries to apply the template, but she doesn't get the interface because she doesn't have permission
        self.login_user("crystaldunn", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button').first.click()
        self.browser.find_by_id('group_membership_settings_button').first.click()
        button = self.browser.find_by_id('browse_membership_templates_button')
        self.assertEquals(len(button), 0)

    def test_apply_template_with_condition(self):

        # set a permission and condition on permission 

        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button').first.click()
        self.browser.find_by_id('forwards_editrole')[0].scroll_to()
        self.browser.find_by_id('forwards_editrole').first.click()
        permissions = [item.text for item in self.browser.find_by_css(".permission-display")]
        self.assertEquals(permissions, [])
        self.browser.find_by_id('add_permission_button').first.click()
        self.browser.select(
            "permission_select", "concord.actions.state_changes.ApplyTemplateStateChange"
        )
        self.browser.find_by_id('save_permission_button').first.click()
        time.sleep(.25)

        perm_element = self.browser.find_by_text("those with role forwards have permission to apply template")
        cond_id = "_".join(["condition"] + perm_element[0]["id"].split("_")[1:])
        self.browser.find_by_id(cond_id).first.click()
        self.browser.select("condition_select", "ApprovalCondition")

        element_containing_role_dropdown = self.browser.find_by_css(".permissionrolefield")[0]
        self.select_from_multiselect("forwards", search_within=element_containing_role_dropdown)
        self.browser.find_by_id('save_condition_button').first.click()
        time.sleep(.25)
        self.browser.find_by_css(".close").first.click()  # close modal

        # new user tries to apply a template
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button').first.click()
        self.browser.find_by_id('group_membership_settings_button').first.click()
        time.sleep(.2)
        self.browser.find_by_id('browse_membership_templates_button').first.click()
        self.browser.find_by_id('apply_template_invite_only').first.click()
        roles_that_can_invite_dropdown = self.browser.find_by_css(".permissionrolefield")[0]
        self.select_from_multiselect("forwards", search_within=roles_that_can_invite_dropdown)
        self.browser.find_by_id('submit_apply_template').first.click()

        # check that the template has not been applied
        self.browser.reload()
        self.browser.find_by_id('group_membership_settings_button').first.click()
        time.sleep(.2)
        permissions = [item.text for item in self.browser.find_by_css("#add_member_permissions * .permission-display")]
        self.assertEquals(permissions, [])

        # log back in as pinoe, approve
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('group_history_button').first.click()
        self.browser.find_by_text("link")[0].click()
        self.assertTrue(self.browser.is_text_present('Please approve or reject this action.'))  
        self.browser.find_by_css("#btn-radios-1 > label:nth-child(1) > span").first.click()
        time.sleep(.25)
        self.browser.find_by_id('save_approve_choice').first.click()

        # check that the template has been applied
        time.sleep(.25)
        self.browser.reload()
        self.browser.back()
        self.browser.back()
        self.browser.find_by_id('governance_button').first.click()
        self.browser.find_by_id('group_membership_settings_button').first.click()
        time.sleep(.25)
        permissions = [item.text for item in self.browser.find_by_css("#add_member_permissions * .permission-display")]
        self.assertEquals(permissions, ["those with role forwards have permission to add members to community"])


class MembershipTestCase(BaseTestCase):

    def setUp(self):
        # Basic setup
        self.create_users()
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

        # generate templates
        from concord.actions.template_library import create_all_templates
        create_all_templates()

    def test_anyone_can_join(self):

        # we start with 4 members
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button').first.click()
        self.browser.find_by_id('members_member_count')[0].scroll_to()
        self.assertEquals(self.browser.find_by_id('members_member_count')[0].text, "4 people")

        # apply anyone can join template
        self.browser.find_by_id('group_membership_settings_button').first.click()
        time.sleep(.2)
        self.browser.find_by_id('browse_membership_templates_button').first.click()
        self.browser.find_by_id('apply_template_anyone_can_join').first.click()
        self.browser.find_by_id('submit_apply_template').first.click()

        # check template was applied
        self.browser.reload()
        self.browser.find_by_id('group_membership_settings_button').first.click()
        time.sleep(.2)
        permissions = [item.text for item in self.browser.find_by_css("#add_member_permissions * .permission-display")]
        self.assertEquals(permissions, ["anyone has permission to add members to community"])

        # random person can join
        self.login_user("midgepurce", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button').first.click()
        self.browser.find_by_id("join_group_button").first.click()
        time.sleep(.25)

        # we should now have 5 members, not 4
        self.browser.find_by_id('members_member_count')[0].scroll_to()
        self.assertEquals(self.browser.find_by_id('members_member_count')[0].text, "5 people")

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
        self.browser.find_by_id('browse_membership_templates_button').first.click()
        self.browser.find_by_id('apply_template_invite_only').first.click()
        roles_that_can_invite_dropdown = self.browser.find_by_css(".permissionrolefield")[0]
        self.select_from_multiselect("forwards", search_within=roles_that_can_invite_dropdown)
        self.browser.find_by_id('submit_apply_template').first.click()

        # check that the template has been applied
        self.browser.reload()
        self.browser.find_by_id('group_membership_settings_button').first.click()
        time.sleep(.2)
        permissions = [item.text for item in self.browser.find_by_css("#add_member_permissions * .permission-display")]
        self.assertEquals(permissions, ["those with role forwards have permission to add members to community"])

        # Midge can't join
        self.login_user("midgepurce", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button').first.click()
        time.sleep(.25)
        self.assertEquals(len(self.browser.find_by_id("join_group_button")), 0)

        # but Christen, a forward, can invite her
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button').first.click()
        self.browser.find_by_id('group_membership_display_button').first.click()
        time.sleep(.5)
        self.browser.find_by_id('add_member_button').first.click()
        time.sleep(.25)
        self.select_from_multiselect(selection="midgepurce")
        time.sleep(.5)
        self.assertEquals(["midgepurce"], self.get_selected_in_multiselect())
        self.browser.find_by_id('save_add_member_button').first.click()
        time.sleep(.5)
        self.browser.find_by_css(".close").first.click()  # close modal
        self.browser.find_by_id('members_member_count')[0].scroll_to()
        self.assertEquals(self.browser.find_by_id('members_member_count').text, "5 people")

    def test_anyone_can_request_to_join(self):

        # we start with 4 members
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button').first.click()
        self.browser.find_by_id('members_member_count')[0].scroll_to()
        self.assertEquals(self.browser.find_by_id('members_member_count')[0].text, "4 people")

        # apply anyone can join template
        self.browser.find_by_id('group_membership_settings_button').first.click()
        time.sleep(.2)
        self.browser.find_by_id('browse_membership_templates_button').first.click()
        self.browser.find_by_id('apply_template_anyone_can_request_to_join').first.click()
        roles_that_can_approve_dropdown = self.browser.find_by_css(".permissionrolefield")[0]
        self.select_from_multiselect("forwards", search_within=roles_that_can_approve_dropdown)
        self.browser.find_by_id('submit_apply_template').first.click()

        # check template was applied
        self.browser.reload()
        self.browser.find_by_id('group_membership_settings_button').first.click()
        time.sleep(.2)
        permissions = [item.text for item in self.browser.find_by_css("#add_member_permissions * .permission-display")]
        self.assertEquals(permissions, ["anyone has permission to add members to community"])
        condition = self.browser.find_by_text("on the condition that one person needs to approve this action")
        self.assertEquals(len(condition), 1)

        # random person can request but they are not added yet
        self.login_user("midgepurce", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('governance_button').first.click()
        self.browser.find_by_id("join_group_button").first.click()
        time.sleep(.25)
        self.browser.find_by_id('members_member_count')[0].scroll_to()
        self.assertEquals(self.browser.find_by_id('members_member_count')[0].text, "4 people")

        # Christen Press, with role forwards, approves
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('group_history_button').first.click()
        self.browser.find_by_text("link").first.click()
        self.assertTrue(self.browser.is_text_present('Please approve or reject this action.'))  
        self.browser.find_by_css("#btn-radios-1 > label:nth-child(1) > span").first.click()
        time.sleep(.25)
        self.browser.find_by_id('save_approve_choice').first.click()
        time.sleep(.25)
        text = "You have approved midgepurce's action. Nothing further is needed from you."
        self.assertTrue(self.browser.is_text_present(text)) 

        # we should now have 5 members, not 4
        self.browser.reload()
        self.browser.back()
        self.browser.back()
        self.browser.find_by_id('governance_button').first.click()
        self.browser.find_by_id('members_member_count')[0].scroll_to()
        self.assertEquals(self.browser.find_by_id('members_member_count')[0].text, "5 people")

    # TODO: suite of comments test cases


class ListTestCase(BaseTestCase):

    def setUp(self):

        # Basic setup
        self.create_users()
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

        from selenium.webdriver.common.keys import Keys

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
        self.browser.fill('row_contents', 'Chicago Red Stars')
        self.browser.find_by_id('add_row_save_button').first.click()
        self.assertTrue(self.browser.is_text_present('Chicago Red Stars'))
        self.browser.find_by_id('add_row_button').first.click()
        self.browser.fill('row_contents', 'NJ Sky Blue')
        self.browser.find_by_id('index')[0].type(Keys.RIGHT)
        self.browser.find_by_id('add_row_save_button').first.click()
        self.browser.find_by_id('add_row_button').first.click()
        self.browser.fill('row_contents', 'Washington Spirit')
        self.browser.find_by_id('add_row_save_button').first.click()
        time.sleep(.5)
        teams = [team.text for team in self.browser.find_by_xpath("//td")]
        teams = list(filter(lambda x: x not in ["edit delete", "0", "1", "2", "3"], teams))
        self.assertEquals(teams, ["Washington Spirit", "Chicago Red Stars", "NJ Sky Blue"])

        # edit a row
        self.browser.find_by_id('edit_row_2').first.click()
        self.browser.fill('row_contents', 'Sky Blue FC')
        self.browser.find_by_id('edit_row_save_button').first.click()
        teams = [team.text for team in self.browser.find_by_xpath("//td")]
        teams = list(filter(lambda x: x not in ["edit delete", "0", "1", "2", "3"], teams))
        self.assertEquals(teams, ["Washington Spirit", "Chicago Red Stars", "Sky Blue FC"])

        # delete a row
        self.browser.find_by_id('delete_row_2').first.click()
        time.sleep(.5)
        teams = [team.text for team in self.browser.find_by_xpath("//td")]
        teams = list(filter(lambda x: x not in ["edit delete", "0", "1", "2", "3"], teams))
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
        self.browser.fill('row_contents', 'Washington Spirit')
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